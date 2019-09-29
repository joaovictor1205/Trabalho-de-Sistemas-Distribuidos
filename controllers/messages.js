const messagesFile = 'archive/messages.json';
const fs = require('fs');

module.exports.getMessages = function(server, wss, sender, message) {
  if (fs.existsSync(messagesFile)) {
    let messagesData = fs.readFileSync(messagesFile, 'utf8');
    let messages = JSON.parse(messagesData);
    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.GET_MESSAGES,
      data: { messages }
    }));
  }
};

module.exports.sendMessage = function(server, wss, sender, message) {
  let flag = true;
  let username = message.data.username;
  let sentMessage = message.data.message;
  let userType = message.data.userType;

  try {
    if (fs.existsSync(messagesFile)) {
      let messagesData = fs.readFileSync(messagesFile, 'utf8');
      let messages = JSON.parse(messagesData);
      messages.push({
        username,
        userType,
        message: sentMessage
      });
      fs.writeFileSync(messagesFile, JSON.stringify(messages), {flag: 'w+'});
    } else {
      let messages = [{
        username,
        userType,
        message: sentMessage
      }];
      fs.writeFileSync(messagesFile, JSON.stringify(messages), {flag: 'w+'});
    }
  } catch(err) {
    flag = false;
  }

  if (!flag) {
    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.SEND_MESSAGE,
      data: { status: false }
    }));
  }

  wss.broadcast({
    type: MESSAGE_TYPES.RECEIVE_MESSAGE,
    data: {
      username: username,
      userType,
      message: sentMessage
    }
  });
};
