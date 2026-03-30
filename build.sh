#!/bin/bash

docker_registry='ghcr.io/mta-tech'
artifact_id='kai'

if [ $# -eq 0 ]; then
    read -p "No tag provided. Enter tag(s) to build and push (default: dev): " TAGS_INPUT
    if [ -z "$TAGS_INPUT" ]; then
        TAGS=("dev")
    else
        read -ra TAGS <<< "$TAGS_INPUT"
    fi
    read -p "Confirm build and push to $docker_registry/$artifact_id with tag(s): ${TAGS[*]}? (Y/n): " confirm
    if [[ "$confirm" == "n" || "$confirm" == "N" ]]; then
        echo "Aborting."
        exit 1
    fi
else
    TAGS=("$@")
fi

FIRST_TAG="${TAGS[0]}"

echo "Building and pushing with tags: ${TAGS[*]}"

# Build the docker image with the first tag
docker build --platform=linux/amd64 --no-cache -f Dockerfile -t $docker_registry/$artifact_id:$FIRST_TAG .

# Tag and push for all specified tags
for TAG in "${TAGS[@]}"; do
    if [ "$TAG" != "$FIRST_TAG" ]; then
        docker tag $docker_registry/$artifact_id:$FIRST_TAG $docker_registry/$artifact_id:$TAG
    fi
    docker push $docker_registry/$artifact_id:$TAG
done