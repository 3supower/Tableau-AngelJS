var express = require('express');
var router = express.Router();
var r = require('rethinkdb');

var p = r.connect({host: 'angel.tsi.lan', db: 'MyDB'});

/* GET users listing. */
router.get('/', function(req, res, next) {
    // res.io.emit("socketToMe", "users");
    res.render('users', {title: 'My Case List'});
});

router.get('/user-list', function(req, res, next) {
    p.then(function(conn) {
        r.table('table1').run(conn).then(function (cursor) {
            return cursor.toArray();
            // return cursor.each();
        }).then(function(results){
            res.render('user-list', {title: 'User List', userData: results});
        });
    });
});

module.exports = router;