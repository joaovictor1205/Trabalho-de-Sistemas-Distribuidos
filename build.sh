#!/usr/bin/env bash

# First argument -> hard / soft
# Second argument -> dae / it
# Third argument -> number of backend servers

echo "Parsing Arguments"
while [[ "$#" -gt 0 ]]
do
    case $1 in
        -b|--build)
            BUILD="$2"
            ;;
        -m|--mode)
            MODE="$2"
            ;;
        -s|--servers)
            SERVERS="$2"
            ;;
    esac
    shift
done

echo "Copying Proto"
cp proto/API.proto backend/proto/
cp proto/API.proto frontend/app/proto/

echo "Deleting Containers"
docker container rm -f nerd_room_frontend
docker container ls -a | awk '{ print $1,$2 }' | grep nerd_room_backend_img | awk '{ print $1 }' | xargs -I {} docker container rm -f {}

echo "Deleting Volumes"
docker volume ls | awk '{ print $1,$2 }' | grep nerd_room_volume | awk '{ print $2 }' | xargs -I {} docker volume rm -f {}

if [ "$BUILD" == "hard" ] ; then
    echo "Building Images"
    docker image build -t nerd_room_backend_img backend/
    docker image build -t nerd_room_frontend_img frontend/

    echo "Deleting Network"
    docker network rm nerd_room_net

    echo "Creating Network"
    docker network create --driver bridge nerd_room_net
fi

sleep 3

for ((i = 0; i < SERVERS; i++));
do
    CONTAINER_NAME="nerd_room_backend${i}"
    VOLUME_NAME="nerd_room_volume${i}"
    INITIAL_PORT=50051
    OUT_PORT=$(($INITIAL_PORT + $i))
    echo $CONTAINER_NAME

    docker volume create ${VOLUME_NAME}

    if [ "$MODE" == "dae" ] ; then
        docker run -i -p 127.0.0.1:$OUT_PORT:50051 \
            -v ${VOLUME_NAME}:/code/archive \
            --env ID_SERVER=${i} --env NUM_SERVERS=${SERVERS} --env INITIAL_PORT=${INITIAL_PORT} \
            --name "${CONTAINER_NAME}" --network nerd_room_net \
            nerd_room_backend_img &
    else
        docker run -d -p 127.0.0.1:$OUT_PORT:50051 \
            -v ${VOLUME_NAME}:/code/archive \
            --env ID_SERVER=${i} --env NUM_SERVERS=${SERVERS} --env INITIAL_PORT=${INITIAL_PORT} \
            --name "${CONTAINER_NAME}" --network nerd_room_net \
            nerd_room_backend_img
    fi
done

sleep 5

if [ "$MODE" == "dae" ] ; then
    docker run -d -p 5000:5000 --name nerd_room_frontend --network nerd_room_net nerd_room_frontend_img
else
    docker run -i -p 5000:5000 --name nerd_room_frontend --network nerd_room_net nerd_room_frontend_img &
fi
