var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  console.log('I am index router. I will emit the socket now!')
  res.io.emit("fromRouter", "gogogo!");
  res.io.emit("mydata", 'hohoho');
  res.render('index', { title: 'Team Chat', yoyoyo: 'Test', s_time: new Date().getTime() });
  // res.send('respond with a resource.');
});

module.exports = router;
