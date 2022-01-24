var r = require('rethinkdb')

r.connect({host: 'angel.tsi.lan'}, function(err, conn) {

    if(err) throw err;
    r.dbList().run(conn, function(err, res) {
        if(err) throw err;
        console.log(res);
    });

    r.db('MyDB').tableList().run(conn, function(err, res) {
        if(err) throw err;
        console.log(res);
    });

    /*
    r.db('MyDB').table('table1').run(conn, function(err, res) {
        if(err) throw err;
        console.log(res)
    });
    */

    r.db('MyDB').table('table1').changes().run(conn, function (err, cursor) {
        if(err) throw err;
        cursor.each(function(err, item) {
            if(err) throw err;
            console.log(item);
        });
    });
   // conn.close(function(err) { if (err) throw err; })
});
