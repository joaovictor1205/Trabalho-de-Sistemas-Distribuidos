module.exports = function(app){

    app.get('/', (req, res) => {
        res.render('./templates/login.html');
    });

    app.get('/login', (req, res) => {
        res.render('./templates/login.html');
    });

}