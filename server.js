const serverVariables = require('./server/configserver.js')
const app = serverVariables.app;
const io = serverVariables.io;
const server = serverVariables.server;

let messages= [];

io.on('connection', socket => {
    
    console.log(`Conection with ${socket.id} socket`);

    socket.emit('showPreviousMessages', messages);

    socket.on('sendMessage', data => {

        messages.push(data);
        socket.broadcast.emit('receivedMessage', data);

    });

});

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));