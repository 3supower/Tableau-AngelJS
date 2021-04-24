const http = require('http');
const fs = require('fs').promises;
const express = require('express');
const chance = require('chance').Chance();
const shuffleArray = require("shuffle-array");

const app = express()
const hostname = '127.0.0.1';
const port = 80;

const server = http.createServer((req, res) => {
  // res.statusCode = 200;
  // res.setHeader('Content-Type', 'text/plain');
  // res.end('Hello World. Angle is running NodeJS');

  // res.setHeader("Content-Type", "text/html");
  // res.end(`<html><body><h1>This is HTML</h1></body></html>`);
  fs.readFile(__dirname + "/index.html")
    .then(contents => {
      res.setHeader("Content-Type", "text/html");
      res.writeHead(200);
      res.end(contents);
    })
    .catch(err => {
        res.writeHead(500);
        res.end(err);
        return;
    });
});

server.listen(port, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});