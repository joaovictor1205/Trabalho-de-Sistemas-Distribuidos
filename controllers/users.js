const bcrypt = require('bcrypt');
const fs = require('fs');

const usersFile = 'archive/users.json';
const userTypes = {
  EMPLOYEE: 0,
  RECRUITER: 1
};

async function hashPassword(password) {
  const saltRounds = 10;

  return await new Promise((resolve, reject) => {
    bcrypt.hash(password, saltRounds, function(err, hash) {
      if (err) reject(err);
      resolve(hash)
    });
  })
}

module.exports.registerUser = async function(server, wss, sender, message) {
  console.log(server)
  let flag = true;
  let user = message.data;
  user.password = await hashPassword(user.password);

  try {
    if (fs.existsSync(usersFile)) {
      fs.readFile(usersFile, 'utf8', (err, data) => {
        if (err) throw err;

        //TODO SEARCH IN THE FILE
      });
    } else {
      users = [user];
      fs.writeFileSync(usersFile, JSON.stringify(users), {flag: 'w+'});
    }
  } catch(err) {
    flag = false;
  }

  sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.REGISTER_USER,
    data: flag
  }));
};

module.exports.loginUser = function(server, wss, sender, message) {

};
