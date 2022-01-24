r = require('rethinkdb');

var connection = null;
r.connect({host: 'angel.tsi.lan', port: 28015}, (err, conn)=>{
    if (err) throw err;
    connection = conn;
})

r.table('MyDB').run(connection, (err, cursor) => {
    if (err) throw err;
    cursor.toArray((err, result) => {
        if (err) throw err;
        console,log(JSON.stringify(result, null, 2));
    });
});