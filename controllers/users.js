const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const fs = require('fs');

const secretJWT = 'jkhgjkg345kuihfdf,nmn354435kjwmsdfsd';
const usersFile = 'archive/users.json';
const userTypes = {
  EMPLOYEE: 0,
  RECRUITER: 1
};

async function comparePassword(password, hash) {
  return await new Promise((resolve, reject) => {
    bcrypt.compare(password, hash, function(err, res) {
      if (err) reject(err);
      resolve(res);
    });
  })
}

async function hashPassword(password) {
  const saltRounds = 10;

  return await new Promise((resolve, reject) => {
    bcrypt.hash(password, saltRounds, function(err, hash) {
      if (err) reject(err);
      resolve(hash);
    });
  })
}

module.exports.registerUser = async function(server, wss, sender, message) {
  let flag = true;
  let user = message.data;
  user.password = await hashPassword(user.password);

  try {
    if (fs.existsSync(usersFile)) {
      let usersData = fs.readFileSync(usersFile, 'utf8');
      let usersObj = JSON.parse(usersData);

      if(usersObj.find(userAux => userAux.username === user.username)) {
        flag = false;
      }

      usersObj.push(user);
      fs.writeFileSync(usersFile, JSON.stringify(usersObj), {flag: 'w+'});
    } else {
      let users = [user];
      fs.writeFileSync(usersFile, JSON.stringify(users), {flag: 'w+'});
    }
  } catch(err) {
    flag = false;
  }

  if (!flag) {
    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.REGISTER_USER,
      data: {
        status: false
      }
    }));
  }

  let token = jwt.sign({username: user.username}, secretJWT, {
    expiresIn: 60*60*24
  });

  sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.REGISTER_USER,
    data: {
      status: true,
      token
    }
  }));
};

module.exports.loginUser = async function(server, wss, sender, message) {
  let flag = true;
  let user = message.data;

  try {
    if (fs.existsSync(usersFile)) {
      let usersData = fs.readFileSync(usersFile, 'utf8');
      let users = JSON.parse(usersData);

      let userAux = users.find(obj => obj.username === user.username);

      if (!userAux) flag = false;
      else {
        let resPassword = await comparePassword(user.password, userAux.password);
        if (!resPassword) flag = false;
      }
    } else {
      flag = false;
    }
  } catch(err) {
    flag = false;
  }

  if (!flag) {
    return sender.send(JSON.stringify({
      type: global.MESSAGE_TYPES.LOGIN_USER,
      data: {
        status: false
      }
    }));
  }

  let token = jwt.sign({username: user.username}, secretJWT, {
    expiresIn: 30
  });

  sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.LOGIN_USER,
    data: {
      status: true,
      token
    }
  }));
};
