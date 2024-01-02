#!/bin/bash
docker buildx build --platform linux/amd64 -t quangdvn/convert-auth .
docker push quangdvn/convert-auth:latest

cd ./k8s
kubectl delete -f .
kubectl apply -f .