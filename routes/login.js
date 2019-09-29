module.exports = function (app) {
  app.get('/login', (req, res) => {
    let context = { MESSAGE_TYPES: JSON.stringify(global.MESSAGE_TYPES) };
    res.render('./templates/login', context);
  });
};
