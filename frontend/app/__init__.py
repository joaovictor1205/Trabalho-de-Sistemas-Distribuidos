from flask import Flask
import grpc

app = Flask(__name__)

from app import views
from app.proto import API_pb2_grpc

channel = grpc.insecure_channel('backend:50051')
stub = API_pb2_grpc.APIStub(channel)
