const serverVariables = require('./server/configserver.js')
const io = serverVariables.io;
const server = serverVariables.server;
const archive = require('fs');

let messages= [];

io.on('connection', socket => {
    
    console.log(`Conection with ${socket.id} socket`);

    socket.emit('showPreviousMessages', messages);

    socket.on('sendMessage', data => {

        messages.push(data);
        socket.broadcast.emit('receivedMessage', data);

        var myJSON = JSON.stringify(data);
        archive.readFile('./public/archive/messages.json', 'utf-8', function(err, data) {
            if (err) throw err
        
            var arrayOfObjects = JSON.parse(data);
            arrayOfObjects.chat.push(myJSON);
            var array = JSON.stringify(arrayOfObjects);

            archive.writeFile('./public/archive/messages.json', array , 'utf-8', function(err) {
                if (err) throw err
            });
        
        });

    });

});

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));