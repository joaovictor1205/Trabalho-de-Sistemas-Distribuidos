FROM python:3

RUN apt-get install curl
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /code
WORKDIR /code
ADD . /code

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./proto/API.proto

EXPOSE 50051
