FROM nikolaik/python-nodejs:latest

RUN apt-get install curl autoconf automake libtool make g++ unzip
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /code
WORKDIR /code
ADD . /code

ENV PYTHONUNBUFFERED 1

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./app/proto/API.proto

EXPOSE 5000
CMD ["python", "-u", "run.py"]
