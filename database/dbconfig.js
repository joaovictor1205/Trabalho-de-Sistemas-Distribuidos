const mongoose = require('mongoose');

module.exports = function(){
    return mongoose.connect('mongodb://localhost/trabalhodesd');
};