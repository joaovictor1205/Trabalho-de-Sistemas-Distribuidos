const express = require('express')
const path = require('path')
const consign = require('consign')

const app = express();
const server = require('http').createServer(app)

app.use(express.static(path.join(__dirname, '../public')));
app.set('view engine', 'ejs')
app.set('views', path.join(__dirname, '../public'));


consign().include('./routes/').then('./controllers/').into(app);

module.exports = { app, server }
