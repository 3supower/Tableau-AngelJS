# -*- coding: utf-8 -*-

from cgi import test
import subprocess
import json
import re
import time
import pprint
import datacompy
import logging
import pandas as pd
from rethinkdb import RethinkDB

# logging.basicConfig(filename='catchpy.log', level=logging.DEBUG)

r = RethinkDB()
conn = r.connect(host='angel.tsi.lan', db='MyDB')
# conn = r.connect(host='3ef0c5d6ba19477.tsi.lan', db='DevilCASE')

query = '''
SELECT 
	Id, CaseNumber, Priority, Case_Age__c, Status, Description, Preferred_Case_Language__c, 
	Case_Preferred_Timezone__c, Tier__c, Category__c, Product__c, Subject, First_Response_Complete__c, 
	CreatedDate, Entitlement_Type__c, Plan_of_Action_Status__c, Case_Owner_Name__c,
    IsEscalated, Escalated_Case__c,
    ClosedDate, IsClosed, isClosedText__c, 
    AccountId, Account.Name, Account.CSM_Name__c, Account.CSM_Email__c,
    (SELECT CreatedDate, field, OldValue, NewValue, CreatedById FROM Histories WHERE CreatedDate=TODAY and field='Owner')
FROM Case 
WHERE
	RecordTypeId='012600000000nrwAAA' AND
	( (IsClosed=False) OR (IsClosed=True AND ClosedDate=TODAY) ) AND
	Preferred_Support_Region__c ='APAC' AND 
	Preferred_Case_Language__c != 'Japanese' AND 
	Tier__c != 'Admin'
'''


soql = re.sub("\n", " ", query)
old_dict = []
old_df = pd.DataFrame()
initial_loading = True

if old_df.empty:
    print('OLD DataFrame is empty!')

while True:
    result_is_empty = True
    while result_is_empty:
        print('Query starts...')
        start_time = time.time()
        try:
            result = subprocess.run(
                ['sfdx', 'force:data:soql:query', '-q', soql, '-u', 'mypyOrg', '--json'],
                shell=True,
                capture_output=True
            )
            print('Query ended...')
            end_time = time.time()
            print('Elapsed... ' + str(round(end_time - start_time)) + " sec")
            result_dict = json.loads(result.stdout)
            result_is_empty = False
        except:
            print("Query got error")

    # Error handling - https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_plugins.meta/sfdx_cli_plugins/cli_plugins_customize_errors.htm
    # if (new_dict == None or len(new_dict) <= 0):
    if (result_dict['status'] == 1): # status == 1 means Error
        print('There is an error while querying')
        # print(item_dict['name'] + ": " + item_dict['message'])
        print(result_dict['stack'])
    else: # assume status == 0
        new_dict = sorted(result_dict['result']['records'], key = lambda x: x['CaseNumber'])
        print('Total Size: ' + str(result_dict['result']['totalSize']))
        print('Records Size: ' + str(len(new_dict)))

        df = pd.DataFrame(new_dict)
                
        df_filtered = df.loc[df["Case_Owner_Name__c"].isnull() | (df["Case_Owner_Name__c"].notnull() & df["Histories"].notnull()),[
            "Id",
            "CaseNumber",
            "Case_Age__c", 
            "Status", 
            "Priority", 
            "Entitlement_Type__c",
            "First_Response_Complete__c", 
            "Product__c", 
            "Category__c",
            "Case_Owner_Name__c", 
            "IsEscalated",
            "Preferred_Case_Language__c",
            "Case_Preferred_Timezone__c",
            "Subject",
            "Histories",
            "Account"
        ]]

        exploded = df_filtered.Account.apply(json.dumps).apply(json.loads).apply(pd.Series).drop(columns='attributes')
        
        new_df = pd.concat([df_filtered, exploded], axis=1)
        new_df.columns = new_df.columns.str.lower()
        # new_df["id"] = new_df['casenumber']
        # print(new_df.columns)

        # SAMPLE DATAFRAME
        # new_df = pd.DataFrame({'CaseNumber': [1111, 2222, 4444], 'Case_Age__c': [1,3,1], 'Status': ['Active', 'Active','Active']})
        # old_df = pd.DataFrame({'CaseNumber': [1111, 2222, 3333], 'Case_Age__c': [2,2,1], 'Status': ['Active', 'Active', 'Active']})

        if old_df.empty:
            print('OLD DataFrame is empty!')
        else:
            df1 = new_df
            df2 = old_df

            compare = datacompy.Compare(
            df1,
            df2,
            join_columns='CaseNumber', #You can also specify a list of columns
            abs_tol=0.0001,
            rel_tol=0,
            df1_name='new',
            df2_name='old',
            ignore_case=True,
            cast_column_names_lower=True
            )

            # Detect new cases - Adding new rows into the existing table
            if compare.df1_unq_rows.empty:
                print("No new case!!")
                logging.warning("no new case")
            else:
                logging.error('Yes! We got a new CASE!')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ADD ROWS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(compare.df1_unq_rows)
                new_case = compare.df1_unq_rows.fillna('').to_dict(orient="records")
                print(new_case)
                r.table("table1").insert(new_case).run(conn)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ADD ROWS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            
            
            # Detect expired case - Removing rows from the existing table
            print("==========================================================================================")
            print("Expired cases (closed yesterday) - To remove from the table")
            if compare.df2_unq_rows.empty:
                print("No expired case!!")
            else:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@REMOVE ROWS@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(compare.df2_unq_rows)
                old_case = compare.df2_unq_rows.fillna('').to_dict(orient="records")
                print(old_case)
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@REMOVE ROWS@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("==========================================================================================")
            
            # Detecting changed cases - Modifying/Replacing rows to the existing tableau
            changes = compare.all_mismatch()
            if changes.empty:
                print("No Changes!")
            else:
                changed_data = changes.filter(regex='df1')
                changed_data.columns = changed_data.columns.str.replace('_df1','')
                print("Changed Data")
                print(changed_data)

                for namedTuple in changed_data.fillna('').itertuples(index=False):
                    dictRow = namedTuple._asdict()
                    print("Existing record in DB")
                    print(r.table('table1').get(dictRow['id']).run(conn))
                    print("Updating record")
                    update = r.table('table1').get(dictRow['id']).update(dictRow).run(conn)
                    print(update)
                    print("New record in DB")
                    print(r.table('table1').get(dictRow['id']).run(conn))

        ## RethinkDB
        # When the program is firstly loaded
        # new_df = new_df.fillna('')
        conversion = new_df.fillna('').to_dict(orient='records')

        # print(conversion)


        if initial_loading:
            r.table('table1').delete().run(conn)
            r.table('table1').insert(conversion).run(conn)
            initial_loading = False

        old_df = new_df
        old_dict = new_dict
    print('----------------------------------------------------------------------')
