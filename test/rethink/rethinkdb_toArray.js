var r = require('rethinkdb')
var results = [];

/*
r.connect({host: 'angel.tsi.lan', db: 'MyDB'}, function(err, conn) {

    r.table('table1').run(conn, function (err, cursor) {
        if(err) throw err;
        cursor.toArray(function(err, results) {
            if(err) throw err;
            console.log(results);
            // processResults(results);
        });
    });
});
*/

r.connect({host: 'angel.tsi.lan', db: 'MyDB'}, function(err, conn) {

    r.table('table1').run(conn, function (err, cursor) {
        // if(err) throw err;
        results = cursor.toArray(function(err, res){
            // if(err) throw err;
            console.log(res);
            results = res;
        });
        // console.log(results);
    });
});

console.log(results);
console.log('haha');