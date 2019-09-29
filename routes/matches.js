module.exports = function (app) {
  app.get('/matches', (req, res) => {
    let context = {
      MESSAGE_TYPES: JSON.stringify(global.MESSAGE_TYPES),
      USER_TYPES: JSON.stringify(global.USER_TYPES)
    };
    res.render('./templates/matches', context);
  });
};
