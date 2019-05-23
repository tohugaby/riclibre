#!/usr/bin/env bash

echo "RICLIBRE_DEPLOY_INFO: Removing previous containers"
docker-compose rm -sf
echo "RICLIBRE_DEPLOY_INFO: Remove riclibre images"
docker-compose down --rmi local
#docker rmi riclibre:latest
echo "RICLIBRE_DEPLOY_INFO: Build and launch containers"
docker-compose up --build -d riclibre
