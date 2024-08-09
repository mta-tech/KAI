#!/bin/bash

# Fetch the list of collections
collections=$(curl -X GET 'http://localhost:8108/collections' -H 'X-TYPESENSE-API-KEY: kai_typesense' | jq -r '.[].name')

# Iterate over each collection and delete it
for collection in $collections; do
  echo "Deleting collection: $collection"
  curl -X DELETE "http://localhost:8108/collections/$collection" -H 'X-TYPESENSE-API-KEY: kai_typesense'
done
