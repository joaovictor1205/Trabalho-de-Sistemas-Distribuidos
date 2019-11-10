from flask import Flask
import grpc
import os

ROOT_API = os.getenv('ROOT_API')

app = Flask(__name__)

from app import views
from app.proto import API_pb2_grpc

channel = grpc.insecure_channel(ROOT_API)
stub = API_pb2_grpc.APIStub(channel)
