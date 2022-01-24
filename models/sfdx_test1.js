const r = require('rethinkdb');

var p = r.connect({ host: 'angel.tsi.lan', db: 'MyDB' });

/*
p.then(function(conn) {
    r.table('table1').run(conn).then(cursor => { 
        return cursor.toArray();
    }).then(function(results) {
        console.log(results);
    });
});
*/

p.then(conn => {
    r.table('table1').delete().run(conn);
    r.table('table1').run(conn).then(cursor => {
        return cursor.toArray();
    }).then(results => {
        if (results.length === 0) {
            console.log('Array is empty!');
        } else {
            console.log(results);
        };
    });
});

const { spawn } = require("child_process");
var query1 = `"
SELECT 
	Id, 
	CaseNumber, 
	Priority, 
	Case_Age__c, 
	Status, 
	Preferred_Case_Language__c, 
	Tier__c, 
	Category__c,
	Product__c, 
	Subject, 
	First_Response_Complete__c, 
	CreatedDate, 
	Entitlement_Type__c, 
	Plan_of_Action_Status__c, 
	Case_Owner_Name__c,
    AccountId,
    Account.Name,
    (SELECT CreatedDate, field, OldValue, NewValue, CreatedById FROM Histories WHERE CreatedDate=TODAY and field='Owner'),
    IsEscalated, Escalated_Case__c
FROM case 
WHERE 
	Id IN (SELECT CaseID FROM CaseHistory ) AND
	RecordTypeId='012600000000nrwAAA' AND
	(Status='New' or Status='Active' or Status='Re-opened') AND 
	Preferred_Support_Region__c ='APAC' AND 
	Preferred_Case_Language__c != 'Japanese' AND 
	Tier__c != 'Admin'
"`.replace(/\n/g, " ");

var opt = "force:data:soql:query";
var org = "vscodeOrg";

const sfdx = spawn("sfdx", [opt, "-q", query1, "-u", org, "--json"], {shell: true});

sfdx.stdout.on("data", data => {
    // console.log(`stdout: ${data}`);
    console.log(typeof(JSON.stringify(data)));
    // console.log(JSON.stringify(data));
    // console.log(`${data}`);

    var str = String.fromCharCode.apply(String, data);
    console.log(JSON.parse(str))

    /*
    p.then(conn => {
        r.table('table1').insert(JSON.stringify(data)).run(conn);
    });
    */
});

sfdx.stderr.on("data", data => {
    console.log(`stderr: ${data}`);
});

sfdx.on('error', (error) => {
    console.log(`error: ${error.message}`);
});

sfdx.on("close", code => {
    console.log(`child process exited with code ${code}`);
});

