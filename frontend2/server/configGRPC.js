const grpc = require('grpc');
const PROTO_PATH = './proto/API.proto';
const protoLoader = require('@grpc/proto-loader');
const packageDefinition = protoLoader.loadSync(
  PROTO_PATH,
  {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
  });

module.exports = (app) => {
  const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
  const API = protoDescriptor.API;
  const grpcClient = new API('localhost:50051', grpc.credentials.createInsecure());
  app.set('grpcClient', grpcClient);
};


/*
let proto = require('../proto/API_pb.js');
let authRequest = new proto.AuthRequest();
console.log(authRequest)
authRequest.setToken('sdfsdf');

grpcClient.Authenticate(authRequest.toObject(), (err, feature) => {
  console.log(err)
  console.log(feature)
})*/
