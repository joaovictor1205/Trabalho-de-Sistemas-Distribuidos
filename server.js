const globalVariables = require('./server/globalVariables');
const serverVariables = require('./server/configserver.js');
const server = serverVariables.server;
const WebSocket = require('ws');

const wss = new WebSocket.Server({port: 40510});

const usersControllers = require('./controllers/users');
const matchesControllers = require('./controllers/matches');
const messagesControllers = require('./controllers/messages');
const authenticationControllers = require('./controllers/authentication');

wss.on('connection', sender => {
  sender.on('message', message => {
    message = JSON.parse(message);

    switch (message.type) {
      case global.MESSAGE_TYPES.AUTHENTICATION:
        authenticationControllers.authenticate(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.REGISTER_USER:
        usersControllers.registerUser(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.LOGIN_USER:
        usersControllers.loginUser(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.GET_MESSAGES:
        messagesControllers.getMessages(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.SEND_MESSAGE:
        messagesControllers.sendMessage(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.OFFER_JOB:
        matchesControllers.offerJob(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.GET_MATCHES:
        matchesControllers.getMatches(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.ACCEPT_MATCH:
        matchesControllers.acceptMatch(server, wss, sender, message);
        break;

      case global.MESSAGE_TYPES.REJECT_MATCH:
        matchesControllers.rejectMatch(server, wss, sender, message);
        break;
    }
  });
});

wss.broadcast = function broadcast(data, sender = null) {
  wss.clients.forEach(function each(client) {
    if (client !== sender) client.send(JSON.stringify(data));
  });
};

const PORT = 3000;
const HOST = 'localhost';
server.listen(PORT, HOST, () => console.log(`Server ON ${HOST}:${PORT}`));
