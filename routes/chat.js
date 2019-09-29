module.exports = function (app) {
    app.get('/chat', (req, res) => {
        let context = { MESSAGE_TYPES: JSON.stringify(global.MESSAGE_TYPES) };
        res.render('./templates/chat', context);
    });
};
