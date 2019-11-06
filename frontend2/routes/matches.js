module.exports = function (app) {
  app.get('/matches', (req, res) => {
    res.render('./templates/matches', context);
  });
};
