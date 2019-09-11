const bcrypt = require('bcryptjs');

const ProjectSchema = new mongoose.Schema({

    name:{
        type: String,
        require: true,
    },

    email:{
        type: String,
        require: true,
    },

    description:{
        type: String,
        require: true,
    },

    password:{
        type: String,
        require: true,
    },

    type:{
        type: String,
        require: true,
    }

});

ProjectSchema.pre('save', async function(next){
    const hash = await bcrypt.hash(this.password, 10);
    this.password = hash;

    next();
});

const Project = mongoose.model('Project', ProjectSchema);

module.exports = Project;