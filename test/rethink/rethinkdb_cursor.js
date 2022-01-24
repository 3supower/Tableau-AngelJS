var r = require('rethinkdb')
var results = []

r.connect({host: 'angel.tsi.lan', db: 'MyDB'}, function(err, conn) {

    r.table('table1').changes().run(conn, function (err, cursor) {
        if(err) throw err;
        /*
        cursor.each(function(err, item) {
            if(err) throw err;
            console.log(item);
        });
        */
        cursor.each(function(err, item) {
            // if(err) throw err;
            console.log(item.CaseNumber);
        });

    });
});