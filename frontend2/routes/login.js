module.exports = function (app) {
  app.get('/login', (req, res) => {
    res.render('./templates/login', context);
  });
};
