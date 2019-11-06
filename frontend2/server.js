const express = require('express');
const path = require('path');
const consign = require('consign');
const bodyParser = require('body-parser');
const configGRPC = require('./server/configGRPC.js');

const app = express();
const server = require('http').createServer(app);

app.use(express.static(path.join(__dirname, './public')));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, './public'));

configGRPC(app);

consign().include('./routes/').then('./controllers/').into(app);

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));
