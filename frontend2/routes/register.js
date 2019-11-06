module.exports = function (app) {
  app.get('/register', (req, res) => {
    res.render('templates/register');
  });

  app.post('/register', (req, res) => {
    app.controllers.users.registerUser(app, req, res);
  });
};
