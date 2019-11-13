#!/usr/bin/env bash

# First argument -> hard / soft
# Second argument -> dae / it
# Third argument -> number of backend servers
# Fourth argument -> keep / purge

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
        -v|--volumes)
            VOLUMES="$2"
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

if [ "$BUILD" == "hard" ] ; then
    if [ "$VOLUMES" == "purge" ] ; then
        echo "Deleting Volumes"
        docker volume ls | awk '{ print $1,$2 }' | grep nerd_room_volume | awk '{ print $2 }' | xargs -I {} docker volume rm -f {}
    fi

    echo "Building Images"
    docker image build -t nerd_room_backend_img backend/
    docker image build -t nerd_room_frontend_img frontend/

    echo "Deleting Network"
    docker network rm nerd_room_net

    echo "Creating Network"
    docker network create --driver bridge nerd_room_net
fi

sleep 3

echo "Building Containers"
for ((i = 0; i < SERVERS; i++));
do
    CONTAINER_NAME="nerd_room_backend${i}"
    VOLUME_NAME="nerd_room_volume${i}"
    INITIAL_PORT=50051
    OUT_PORT=$(($INITIAL_PORT + $i))
    echo $CONTAINER_NAME

    if [ "$VOLUMES" == "purge" ] ; then
        docker volume create ${VOLUME_NAME}
    fi

    if [ "$MODE" == "dae" ] ; then
        docker run -i -p 127.0.0.1:$OUT_PORT:50051 \
            -v ${VOLUME_NAME}:/code/archive \
            --env SERVER_ID=${i} --env HOST=${CONTAINER_NAME} --env PORT=${INITIAL_PORT} \
            --env CONNECT_HOST="nerd_room_backend0" --env CONNECT_PORT="50051" \
            --name "${CONTAINER_NAME}" --network nerd_room_net \
            nerd_room_backend_img &
    else
        docker run -d -p 127.0.0.1:$OUT_PORT:50051 \
            -v ${VOLUME_NAME}:/code/archive \
            --env SERVER_ID=${i} --env HOST=${CONTAINER_NAME} --env PORT=${INITIAL_PORT} \
            --env CONNECT_HOST="nerd_room_backend0" --env CONNECT_PORT="50051" \
            --name "${CONTAINER_NAME}" --network nerd_room_net \
            nerd_room_backend_img
    fi
done

sleep 5

if [ "$MODE" == "dae" ] ; then
    docker run -d -p 5000:5000 --name nerd_room_frontend --env ROOT_API=nerd_room_backend0:50051 --network nerd_room_net nerd_room_frontend_img
else
    docker run -i -p 5000:5000 --name nerd_room_frontend --env ROOT_API=nerd_room_backend0:50051 --network nerd_room_net nerd_room_frontend_img &
fi


echo "Activating watcher for containers"
while sleep 5;
do
    SERVERS=$(docker container ls | grep nerd_room_backend | wc -l)
    RANDOM_ACTIVE_HOST=$(docker container ls --filter status=running --format '{{.Names}}' | grep nerd_room_backend | awk 'NR==1{print $1}')

    for ((i = 0; i < SERVERS; i++));
    do
        CONTAINER_NAME="nerd_room_backend${i}"
        VOLUME_NAME="nerd_room_volume${i}"
        INITIAL_PORT=50051
        OUT_PORT=$(($INITIAL_PORT + $i))

        IS_RUNNING=$(docker container ls --filter status=running | grep $CONTAINER_NAME | wc -l)

        if [ "$IS_RUNNING" == "0" ] ; then
            echo $CONTAINER_NAME

            docker container rm -f $CONTAINER_NAME

            if [ "$MODE" == "dae" ] ; then
                docker run -i -p 127.0.0.1:$OUT_PORT:50051 \
                    -v ${VOLUME_NAME}:/code/archive \
                    --env SERVER_ID=${i} --env HOST=${CONTAINER_NAME} --env PORT=${INITIAL_PORT} \
                    --env CONNECT_HOST=${RANDOM_ACTIVE_HOST} --env CONNECT_PORT=${INITIAL_PORT} \
                    --name "${CONTAINER_NAME}" --network nerd_room_net \
                    nerd_room_backend_img &
            else
                docker run -d -p 127.0.0.1:$OUT_PORT:50051 \
                    -v ${VOLUME_NAME}:/code/archive \
                    --env SERVER_ID=${i} --env HOST=${CONTAINER_NAME} --env PORT=${INITIAL_PORT} \
                    --env CONNECT_HOST=${RANDOM_ACTIVE_HOST} --env CONNECT_PORT=${INITIAL_PORT} \
                    --name "${CONTAINER_NAME}" --network nerd_room_net \
                    nerd_room_backend_img
            fi
        fi
    done
done
