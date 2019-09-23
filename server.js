const serverVariables = require('./server/configserver.js');
const server = serverVariables.server;
const WebSocket = require('ws');
const archive = require('fs');

const wss = new WebSocket.Server({port: 40510});
global.MESSAGE_TYPES = {
  REGISTER_USER: 0,
  LOGIN_USER: 1,
  SEND_MESSAGE: 2,
  SHOW_PREVIOUS_MESSAGES: 3,
  RECEIVED_MESSAGE: 4
};
let messages = [];

const usersControllers = require('./controllers/users');
const messagesControllers = require('./controllers/messages');

wss.on('connection', sender => {
  sender.on('message', message => {
    message = JSON.parse(message);

    switch (message.type) {
      case global.MESSAGE_TYPES.REGISTER_USER:
        usersControllers.registerUser(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.LOGIN_USER:
        usersControllers.loginUser(wss, sender, message);
        break;

      case global.MESSAGE_TYPES.SEND_MESSAGE:
        break;

      case global.MESSAGE_TYPES.RECEIVED_MESSAGE:
        break;

      case global.MESSAGE_TYPES.SHOW_PREVIOUS_MESSAGES:
        break;
    }
  });

  /*sender.send(JSON.stringify({
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
  });*/
});

wss.broadcast = function broadcast(data, sender = null) {
  wss.clients.forEach(function each(client) {
    if (client !== sender) client.send(JSON.stringify(data));
  });
};

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));
