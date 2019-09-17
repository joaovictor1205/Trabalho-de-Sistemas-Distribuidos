const express = require('express')
const path = require('path')
const consign = require('consign')

const app = express();
const server = require('http').createServer(app)

app.use(express.static(path.join(__dirname, '../public')));
app.set('views', path.join(__dirname, '../public'));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html')

consign().include('./routes/').into(app);

module.exports = { app, server }
