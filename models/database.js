var r = require('rethinkdb');
const { connect } = require('./routes');


var connection = r.connect({host: 'angel.tsi.lan', db: 'MyDB'}, function(err, conn) {
    if(err) throw err;
    console.log('MyDB is connected successfully!');
    /*
    console.log('inside');
    console.log(conn);
    console.log('====================================================================================================')
    console.log(connection);
    */
});


/*
var p = r.connect({
    host: 'angel.tsi.lan',
    // port: 28015,
    db: 'MyDB22'
});
p.then(function(conn) {
    // ...
    console.log('MyDB is connected successfully!');
}).error(function(error) {
    // ...
    console.log('MyDB is connected unsuccessfully!!!!');
});
*/

/*
var conn;

r.connect({host: 'angel.tsi.lan', db: 'MyDB'}).then(conn => {
    conn = conn;
    console.log('inside================');
    console.log(conn);
});
*/


/*
let connection = r.connect({host: 'angel.tsi.lan', db: 'MyDB'})
        .then(conn => {
            console.log('inside==============');
            console.log(conn);
          connection = conn;
          console.log('=====================================');
          console.log(connection);
        });
*/

// console.log('outside==================');
// console.log(connection);

module.exports = connection;