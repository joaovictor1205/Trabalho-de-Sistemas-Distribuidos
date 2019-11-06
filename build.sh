#!/usr/bin/env bash

cp proto/API.proto backend/proto/
cp proto/API.proto frontend/app/proto/

if [ "$1" == "hard" ] ; then
   docker-compose up --build
else
   docker-compose up
fi



