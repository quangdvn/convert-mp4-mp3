#!/bin/bash
docker buildx build --platform linux/amd64 -t quangdvn/convert-gateway .
docker push quangdvn/convert-gateway:latest

cd ./k8s
kubectl delete -f .
kubectl apply -f .