#!/bin/bash

version=$(cat VERSION)
docker_registry='ghcr.io/mta-tech'
artifact_id='kai'
full_version=$version

# build the docker image
docker build --platform=linux/amd64 --no-cache -f Dockerfile -t $docker_registry/$artifact_id:latest .

docker push $docker_registry/$artifact_id:latest