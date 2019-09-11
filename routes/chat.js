module.exports = function(app){

    app.get('/chat', (req,res) => {
        res.render('./templates/chat.html');
    });

}