var r = require('rethinkdb')

r.connect({host: 'angel.tsi.lan', db: 'MyDB'}, function(err, conn) {

    r.table('table1').filter({CaseNumber: '06661787'}).delete({returnChanges: true}).run(conn, function(err, res) {
        if(err) throw err;
        console.log(res);
    });
   // conn.close(function(err) { if (err) throw err; })
});