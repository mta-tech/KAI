#!/bin/bash

TAG=$1
docker_registry='ghcr.io/mta-tech'
artifact_id='kai'

if [ -z "$TAG" ]; then
    read -p "No tag provided. Enter tag to build and push (default: dev): " TAG
    if [ -z "$TAG" ]; then
        TAG="dev"
    fi
    read -p "Confirm build and push to $docker_registry/$artifact_id:$TAG? (Y/n): " confirm
    if [[ "$confirm" == "n" || "$confirm" == "N" ]]; then
        echo "Aborting."
        exit 1
    fi
fi

echo "Building and pushing with tag: $TAG"

# build the docker image
docker build --platform=linux/amd64 --no-cache -f Dockerfile -t $docker_registry/$artifact_id:$TAG .

docker push $docker_registry/$artifact_id:$TAG