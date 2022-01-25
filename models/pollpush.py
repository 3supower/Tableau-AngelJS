# -*- coding: utf-8 -*-

import subprocess
import json
import re
import time
import pprint
import datacompy
import logging
import warnings
import pandas as pd
from rethinkdb import RethinkDB

logging.basicConfig(filename='catchpy.log', level=logging.DEBUG)

r = RethinkDB()
conn = r.connect(host='angel.tsi.lan', db='MyDB')

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

# infinite looping of query and update
while True:
    # Check if query result is null(empty)
    result_is_empty = True
    while result_is_empty:
        print('...Query starts...')
        start_time = time.time()
        try:
            result = subprocess.run(
                ['sfdx', 'force:data:soql:query', '-q', soql, '-u', 'mypyOrg', '--json'],
                shell=True,
                capture_output=True
            )
            # Convert the JSON result as a Python Dictionary 
            result_dict = json.loads(result.stdout)            
            result_is_empty = False
        except Exception as e:
            print("Query got an error!")
            print(e)
        print('...Query ended...')
        end_time = time.time()
        elapsed = str(round(end_time - start_time))
        print('Time elapsed: ' + elapsed + " sec")

    # Error handling - https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_plugins.meta/sfdx_cli_plugins/cli_plugins_customize_errors.htm
    # if (new_dict == None or len(new_dict) <= 0):
    if (result_dict['status'] == 1): # status == 1 means Error
        warnings.warn('There is an error while querying')
        # Print out the query error from Salesforce
        # print(item_dict['name'] + ": " + item_dict['message'])
        print(result_dict['stack'])
    else: # assume status == 0
        # Get result data 
        new_dict = sorted(result_dict['result']['records'], key = lambda x: x['CaseNumber'])
        print('Total Size: ' + str(result_dict['result']['totalSize']))
        print('Records Size: ' + str(len(new_dict)))

        # Convert the result dictionary to DataFrame
        df = pd.DataFrame(new_dict)
        # Flatten the nested Account from new_df and removes unnecessary column
        account = df.Account.apply(json.dumps).apply(json.loads).apply(pd.Series).drop(columns='attributes')

        df_filtered = df[[
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
                                "Subject"
                            ]]
        
        new_df = pd.concat([df_filtered, account], axis=1)
        new_df.columns = new_df.columns.str.lower()
        new_df["id"] = new_df['casenumber']
        # print(new_df_filtered.columns)

        if old_df.empty:
            print('OLD DataFrame is empty!')
        else:
            df1 = new_df
            df2 = old_df

            compare = datacompy.Compare(
                df1, df2,
                join_columns='CaseNumber', #You can also specify a list of columns
                abs_tol=0.0001,
                rel_tol=0,
                df1_name='new',
                df2_name='old',
                ignore_case=True,
                cast_column_names_lower=True
            )

            # Detect new cases - add new rows to existing table
            print("==========================================================================================")
            print("New Case Only - To add in the table")
            if compare.df1_unq_rows.empty:
                print("-- No new case!!")
                logging.warning("no new case")
            else:
                logging.error('Yes! We got a new CASE!')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ADD ROWS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(compare.df1_unq_rows)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ADD ROWS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            
            # Detect expired cases - remove rows from existing table
            print("Closed Yesterday - To remove from the table")
            if compare.df2_unq_rows.empty:
                print("-- Nothing to remove from the queue")
            else:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@REMOVE ROWS@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(compare.df2_unq_rows)
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@REMOVE ROWS@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("==========================================================================================")
            
            # Detect changed cases - replace/modify existing table
            print("All Changes")
            # capture mismatches. old =\= new are mismatched that means new changes in these two tables
            changed_rows = compare.all_mismatch()
            clean_new_data = changed_rows.drop(list(changed_rows.filter(regex='df2')), axis='columns')
            clean_new_data.columns = clean_new_data.columns.str.replace('_df1','')
            changed_data = changed_rows.filter(regex='df1')
            # original_data = changed_rows.filter(regex='df2')
            changed_data.columns = changed_data.columns.str.replace('_df1','')
            changed_data = changed_data.fillna('')
            print(changed_data)

            # Update the changed data to RethinkDB
            # It requires to convert DataFrame back to Dictionary format due to RethinkDB operation.
                # Step 1. Convert DataFrame to named Tuple
            for namedTuple in changed_data.itertuples(index=False):
                # Step 2. Convert the Tuple as Dictionary
                dictRow = namedTuple._asdict()
                print("Result from DB")
                print(r.table('table1').get(dictRow['id']).run(conn))
                print("DB updated")
                print(r.table('table1').get(dictRow['id']).update(dictRow).run(conn))

        new_df = new_df.fillna('')
        new_df_dict = new_df.to_dict(orient='records')

        ## RethinkDB
        # When the program is firstly loaded
        if initial_loading:
            r.table('table1').delete().run(conn)
            r.table('table1').insert(new_df_dict).run(conn)
            initial_loading = False

        old_df = new_df
        old_dict = new_dict
    print('----------------------------------------------------------------------')
