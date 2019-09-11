module.exports = function(app){

    app.get('/chatEnterprise', (req,res) => {
        res.render('./templates/chatEnterprise.html');
    });

    app.get('/chatProgrammers', (req,res) => {
        res.render('./templates/chatProgrammers.html');
    });

}