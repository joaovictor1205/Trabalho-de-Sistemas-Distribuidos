const serverVariables = require('./server/configserver.js');
const server = serverVariables.server;
const WebSocket = require('ws');
const archive = require('fs');

const wss = new WebSocket.Server({port: 40510});
const MESSAGE_TYPES = {
  SEND_MESSAGE: 0,
  SHOW_PREVIOUS_MESSAGES: 1,
  RECEIVED_MESSAGE: 2
};
let messages = [];

wss.on('connection', sender => {
  sender.send(JSON.stringify({
    type: MESSAGE_TYPES.SHOW_PREVIOUS_MESSAGES,
    data: messages
  }));

  sender.on('message', message => {
    message = JSON.parse(message);

    if (message.type === MESSAGE_TYPES.SEND_MESSAGE) {
      messages.push(message.data);
      console.log(`Received message => ${message.data}`);

      wss.broadcast({
        type: MESSAGE_TYPES.RECEIVED_MESSAGE,
        data: message.data
      }, sender);

      let myJSON = JSON.stringify(message.data);
      archive.readFile('./public/archive/messages.json', 'utf-8', function (err, data) {
        if (err) throw err

        let arrayOfObjects = JSON.parse(data);
        arrayOfObjects.chat.push(myJSON);
        let array = JSON.stringify(arrayOfObjects);

        archive.writeFile('./public/archive/messages.json', array, 'utf-8', function (err) {
          if (err) throw err
        });

        let arrayMessages = JSON.parse(array);
        // console.log(arrayMessages);
      });
    }
  });
});

wss.broadcast = function broadcast(data, sender=null) {
  wss.clients.forEach(function each(client) {
    if (client !== sender) client.send(JSON.stringify(data));
  });
};

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));
