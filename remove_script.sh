cd ./auth/k8s
kubectl delete -f .
cd ../../

cd ./converter/k8s
kubectl delete -f .
cd ../../

cd ./gateway/k8s
kubectl delete -f .
cd ../../

cd ./rabbit/k8s
kubectl delete -f .
# cd ../../