var r = require('rethinkdb')

console.log('i promise.');
var p = r.connect({host: 'angel.tsi.lan', db: 'MyDB'});

var connection = p.then(conn);

console.log(connection);