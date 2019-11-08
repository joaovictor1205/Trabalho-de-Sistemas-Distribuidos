#!/usr/bin/env bash

docker container stop nerd_room_frontend
docker container ls -a | awk '{ print $1,$2 }' | grep nerd_room_backend_img | awk '{ print $1 }' | xargs -I {} docker container stop {}
