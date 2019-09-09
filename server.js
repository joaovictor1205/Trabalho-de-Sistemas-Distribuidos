const express = require('express')
const path = require('path')

const app = express();
const server = require('http').createServer(app)
const io = require('socket.io')(server);

app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, 'public'));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html')

app.use('/', (req,res) => {
    res.render('templates/index.html');
});

let messages= [];

io.on('connection', socket => {
    
    console.log(`Conection with ${socket.id} socket`);

    socket.emit('showPreviousMessages', messages);


    socket.on('sendMessage', data => {

        messages.push(data);
        socket.broadcast.emit('receivedMessage', data);

    });

});


server.listen(3000, () => console.log('Server ON'));