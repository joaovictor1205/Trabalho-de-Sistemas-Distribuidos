const serverVariables = require('./server/configserver.js')
const io = serverVariables.io;
const server = serverVariables.server;
const archive = require('fs')

let messages= [];

io.on('connection', socket => {
    
    console.log(`Conection with ${socket.id} socket`);

    socket.emit('showPreviousMessages', messages);

    socket.on('sendMessage', data => {

        messages.push(data);
        socket.broadcast.emit('receivedMessage', data);

        let myJSON = JSON.stringify(data);
        archive.readFile('./public/archive/messages.json', 'utf-8', function(err, data) {
            if (err) throw err
        
            let arrayOfObjects = JSON.parse(data);
            arrayOfObjects.chat.push(myJSON);
            let array = JSON.stringify(arrayOfObjects);

            archive.writeFile('./public/archive/messages.json', array , 'utf-8', function(err) {
                if (err) throw err
            });

            let arrayMessages = JSON.parse(array);
            console.log(arrayMessages);

        });

    });



});

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));