#!/usr/bin/env bash

echo "Remove previous containers"
docker-compose down
echo "Remove riclibre image"
docker rmi riclibre:latest
echo "Build and launch containers"
docker-compose up --build -d riclibre
