var express = require('express');
var router = express.Router();
var r = require('rethinkdb');

var p = r.connect({host: 'angel.tsi.lan', db: 'MyDB'});

router.get('/', function(req, res, next) {
    
    // Sending response to client (browser)
    // res.send('respond with a resource.');

    // Sockets - On/Emit

    // Server Side emit.. 
    res.io.emit("routerEmit", "From Server to Client");
    
    // Just like app.js emit when connection occurs
    res.io.on('connection', (client) => {
        res.io.sockets.emit('onloading', 'Hey new commer!!');
        res.io.sockets.emit('test_emit', 'emit from where?')
    });
    
    // Rethink DB result
    p.then(function(conn) {
        
        r.table('table1').run(conn).then(function (cursor) {
            return cursor.toArray();
        }).then(function(results){            
            res.render('cases', {title: 'Case List', userData: results});
        });
    });

    p.then(conn =>{
        r.table('table1').changes().run(conn).then(cursor => {
            cursor.each((err, data) => {
                // const message = data.changes;
                res.io.emit('newchange', data);
                // res.io.sockets.emit('message', message);
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