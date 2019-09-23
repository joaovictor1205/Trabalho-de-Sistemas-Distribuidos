module.exports = function (app) {
  app.get('/register', (req, res) => {
    let context = { MESSAGE_TYPES: JSON.stringify(global.MESSAGE_TYPES) };
    res.render('./templates/register', context);
  });
};
