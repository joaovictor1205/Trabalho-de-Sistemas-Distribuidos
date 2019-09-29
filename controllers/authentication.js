const jwt = require('jsonwebtoken');
const secretJWT = 'jkhgjkg345kuihfdf,nmn354435kjwmsdfsd';
const fs = require('fs');

const usersFile = 'archive/users.json';
const userTypes = {
  EMPLOYEE: 0,
  RECRUITER: 1
};

module.exports.authenticate = function(server, wss, sender, message) {
  let token = message.data.token;

  jwt.verify(token, secretJWT, async (err, decoded) => {
    if (err || !decoded) {
      return sender.send(JSON.stringify({
        type: global.MESSAGE_TYPES.AUTHENTICATION,
        data: { status: false }
      }));
    }

    let flag = true;
    let username = decoded.username;
    let userType;
    if (fs.existsSync(usersFile)) {
      let usersData = fs.readFileSync(usersFile, 'utf8');
      let users = JSON.parse(usersData);

      let userAux = users.find(obj => obj.username === username);

      if (!userAux) flag = false;
      else {
        userType = userAux.userType;
      }
    } else {
      flag = false;
    }

    if (!flag) {
      return sender.send(JSON.stringify({
        type: global.MESSAGE_TYPES.AUTHENTICATION,
        data: { status: false }
      }));
    }

    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.AUTHENTICATION,
      data: {
        status: true,
        user: {
          username,
          userType
        }
      }
    }));
  });
};
