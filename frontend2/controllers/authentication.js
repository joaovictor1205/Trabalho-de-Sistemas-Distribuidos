const jwt = require('jsonwebtoken');
const fs = require('fs');

const usersFile = 'archive/users.json';
const matchesFile = 'archive/matches.json';

module.exports.authenticate = function(server, wss, sender, message) {
  let token = message.data.token;

  jwt.verify(token, global.secretJWT, async (err, decoded) => {
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

    if (userType === global.USER_TYPES.EMPLOYEE) {
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
    }

    let matches = [];
    if (fs.existsSync(matchesFile)) {
      let matchesData = fs.readFileSync(matchesFile, 'utf8');
      let matchesObj = JSON.parse(matchesData);

      let matchesAux = matchesObj.filter(obj => obj.recruiter === username);
      matches = matches.concat(matchesAux);
    }

    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.AUTHENTICATION,
      data: {
        status: true,
        user: {
          username,
          userType,
          matches
        }
      }
    }));
  });
};
