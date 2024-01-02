#!/bin/bash
docker buildx build --platform linux/amd64 -t quangdvn/convert-converter .
docker push quangdvn/convert-converter:latest

cd ./k8s
kubectl delete -f .
kubectl apply -f .