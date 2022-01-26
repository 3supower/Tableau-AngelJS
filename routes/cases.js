var express = require('express');
var router = express.Router();

var r = require('rethinkdb');
var p = r.connect({host: 'angel.tsi.lan', db: 'MyDB'});

router.get('/', function(req, res, next) {
    // Sending response to client (browser)
    // res.send('respond with a resource.');

    // Router Emit to client 
    res.io.on('connection', (client) => {
        // both works
        res.io.sockets.emit('router_emit1', 'this is router emit');
        res.io.emit('router_emit2', 'emit from router')
    });
    
    // Rethink DB result
    // Get all cases - function
    p.then(function(conn) {
        r.table('table1').run(conn).then(function (cursor) {
            return cursor.toArray();
        }).then(function(results){            
            res.render('cases', {title: 'Case List', caseTable: results});
        });
    });

    // Get changes - arrow function
    p.then(conn =>{
        r.table('table1').changes().run(conn).then(cursor => {
            cursor.each((err, data) => {
                res.io.emit('newchange', data);
                // res.io.sockets.emit('newchange', data);
                // res.render('cases', {'change': data});

                // colling whole array when change occurs 퍼포먼스때문에 잠시 보류! 꼭 다시 활성화 할것!!!!!!!!!!!!!!!!!!1
                /*
                r.table('table1').run(conn).then(function (cursor) {
                    return cursor.toArray();
                }).then(function(results){
                    // lookup cases.ejs from views
                    // res.render('cases', {title: 'Case List', userData: results});
                    res.io.emit('userData', results);
                });
                */
            });
        });
    });
});

module.exports = router;