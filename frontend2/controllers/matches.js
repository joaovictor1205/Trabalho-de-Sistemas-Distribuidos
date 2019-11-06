const fs = require('fs');

const matchesFile = 'archive/matches.json';
const usersFile = 'archive/users.json';

module.exports.offerJob = function(server, wss, sender, message) {
  let recruiter = message.data.recruiter;
  let employee = message.data.employee;
  let employeeEmail = '';

  if (fs.existsSync(usersFile)) {
    let usersData = fs.readFileSync(usersFile, 'utf8');
    let users = JSON.parse(usersData);

    let userAux = users.find(obj => obj.username === employee);
    if (userAux) employeeEmail = userAux.email;
  }

  try {
    if (fs.existsSync(matchesFile)) {
      let matchesData = fs.readFileSync(matchesFile, 'utf8');
      let matches = JSON.parse(matchesData);
      matches.push({
        recruiter,
        employee,
        employeeEmail,
        recruiterMatch: true,
        employeeMatch: undefined,
      });
      fs.writeFileSync(matchesFile, JSON.stringify(matches), {flag: 'w+'});
    } else {
      let matches = [{
        recruiter,
        employee,
        employeeEmail,
        recruiterMatch: true,
        employeeMatch: undefined,
      }];
      fs.writeFileSync(matchesFile, JSON.stringify(matches), {flag: 'w+'});
    }
  } catch(err) {
    console.log(err);
  }
};

module.exports.getMatches = function(server, wss, sender, message) {
  let user = message.data.user;

  let matches = [];
  if (fs.existsSync(matchesFile)) {
    let matchesData = fs.readFileSync(matchesFile, 'utf8');
    let matchesObj = JSON.parse(matchesData);

    let matchesAux;
    if (user.userType === global.USER_TYPES.RECRUITER)
      matchesAux = matchesObj.filter(obj => obj.recruiter === user.username);
    else
      matchesAux = matchesObj.filter(obj => obj.employee === user.username);
    matches = matches.concat(matchesAux);
  }

  return sender.send(JSON.stringify({
    type: global.MESSAGE_TYPES.GET_MATCHES,
    data: {
      matches
    }
  }));
};

module.exports.acceptMatch = function(server, wss, sender, message) {
  let recruiter = message.data.recruiter;
  let employee = message.data.employee;

  if (fs.existsSync(matchesFile)) {
    let matchesData = fs.readFileSync(matchesFile, 'utf8');
    let matches = JSON.parse(matchesData);

    let matchIndex = matches.findIndex(obj => obj.recruiter === recruiter && obj.employee === employee);
    matches[matchIndex].employeeMatch = true;
    fs.writeFileSync(matchesFile, JSON.stringify(matches), {flag: 'w+'});
  }
};

module.exports.rejectMatch = function(server, wss, sender, message) {
  let recruiter = message.data.recruiter;
  let employee = message.data.employee;

  if (fs.existsSync(matchesFile)) {
    let matchesData = fs.readFileSync(matchesFile, 'utf8');
    let matches = JSON.parse(matchesData);

    let matchIndex = matches.findIndex(obj => obj.recruiter === recruiter && obj.employee === employee);
    matches[matchIndex].employeeMatch = false;
    fs.writeFileSync(matchesFile, JSON.stringify(matches), {flag: 'w+'});
  }
};
