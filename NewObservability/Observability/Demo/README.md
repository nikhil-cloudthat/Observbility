## Demo-application

Demo application is well instrumented to send metrics, traces and logs to specified endpoint which is alloy.

**How to run Demo-app**

Step 1: Build the Demo application
```
docker build -t demo-app:v1 -f /path/to/Dockerfile .
docker tag demo-app:v1 docker_registry/demo-app:v1
docker push docker_registry/demo-app:v1
```

Step 2: Update image with tag in deployment manifest file.

Step 3: Deploy application in kubernetes
```
kubectl apply -f newapp.yaml
```