const proto = require('../proto/API_pb.js');

module.exports.registerUser = function(app, req, res) {
  let user = req.body;

  let pbUser = new proto.User();
  pbUser.setUsername(user.username);
  // pbUser.setUserType(parseInt(user.userType));
  pbUser.setEmail(user.email);
  pbUser.setPassword(user.password);

  console.log(pbUser.toObject())

  app.settings.grpcClient.RegisterUser(pbUser.toObject(), (err, user) => {
    console.log(err)
    console.log(user);
  });

  /*grpcClient.Authenticate(authRequest.toObject(), (err, feature) => {
    console.log(err)
    console.log(feature)
  })*!/
*/

  /*let flag = true;
  let user = req.body;
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

  let token = jwt.sign({username: user.username}, global.secretJWT, {
    expiresIn: 60 * 60 * 24
  });

  sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.REGISTER_USER,
    data: {
      status: true,
      token
    }
  }));*/
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

  let token = jwt.sign({username: user.username}, global.secretJWT, {
    expiresIn: 60 * 60 * 24
  });

  sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.LOGIN_USER,
    data: {
      status: true,
      token
    }
  }));
};
