# Minikube Setup Guide - Distributive Project

## Overview
This guide walks you through deploying the Distributive Streamlit application with MongoDB to a local Minikube Kubernetes cluster.

## Prerequisites
- Docker Desktop installed and running
- Minikube installed ([Download](https://minikube.sigs.k8s.io/docs/start/))
  - Windows: `choco install minikube`
  - macOS: `brew install minikube`
  - Linux: Follow official instructions
- kubectl installed ([Download](https://kubernetes.io/docs/tasks/tools/))
  - Windows: `choco install kubernetes-cli`
  - macOS: `brew install kubectl`
- Git and this project cloned locally

## Step-by-Step Setup

### Step 1: Start Minikube
```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

**Expected output:**
```
😄  minikube v1.x.x on Windows
✨  Using the docker driver based on user configuration
👍  Starting control plane node minikube in cluster minikube
...
🎉  Done! kubectl is now configured to use "minikube" cluster and "minikube" context by default
```

### Step 2: Configure Docker to use Minikube's Docker Daemon

This is crucial! You must build the image inside Minikube's Docker environment.

**Windows (PowerShell):**
```powershell
minikube docker-env | Invoke-Expression
```

**Windows (cmd):**
```cmd
@FOR /f "tokens=*" %i IN ('minikube docker-env --shell cmd') DO @%i
```

**macOS/Linux (Bash/Zsh):**
```bash
eval $(minikube docker-env)
```

✅ **Verify** that you're using Minikube's Docker:
```bash
docker version
```

You should see the Docker client version, and the Docker server version should indicate Minikube's context.

### Step 3: Build Docker Image Inside Minikube

```bash
docker build -t distributive-app:latest .
```

**Expected output:**
```
Sending build context to Docker daemon  ...
Step 1/... FROM python:3.12-slim
...
Successfully tagged distributive-app:latest
```

✅ **Verify** the image was created:
```bash
docker images | grep distributive
```

You should see:
```
distributive-app   latest   <image-id>   <timestamp>   <size>
```

### Step 4: Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/
```

**Expected output:**
```
deployment.apps/distributive-deployment created
service/distributive-service created
service/mongo-service created
```

### Step 5: Verify Deployment

#### Check Pods Status
```bash
kubectl get pods
```

**Expected output (wait 30-60 seconds for pods to be ready):**
```
NAME                                      READY   STATUS    RESTARTS   AGE
distributive-deployment-xxxxx-xxxxx       2/2     Running   0          45s
distributive-deployment-xxxxx-xxxxx       2/2     Running   0          40s
```

✅ **Both containers (distributive + mongo) should show 2/2 READY**

#### Check Services
```bash
kubectl get services
```

**Expected output:**
```
NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
distributive-service    NodePort    10.x.x.x        <none>        8501:30007/TCP      2m
mongo-service        ClusterIP   10.x.x.x        <none>        27017/TCP           2m
kubernetes           ClusterIP   10.96.0.1       <none>        443/TCP             10m
```

#### Check Deployments
```bash
kubectl get deployments
```

**Expected output:**
```
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
distributive-deployment    2/2     2            2           3m
```

### Step 6: Troubleshoot if Issues Arise

#### Pods are in Pending state
```bash
kubectl describe pod <pod-name>
```

✅ **Fix:** Usually means Minikube doesn't have enough resources. Restart with more memory:
```bash
minikube delete
minikube start --driver=docker --memory=6144 --cpus=4
```

#### ImagePullBackOff error
```bash
kubectl describe pod <pod-name>
```

✅ **Fix:** The image wasn't built in Minikube's Docker. Verify:
```bash
minikube docker-env | Invoke-Expression  # Windows PowerShell
eval $(minikube docker-env)               # macOS/Linux
docker images | grep distributive
docker build -t distributive-app:latest .
```

#### Containers keep restarting (CrashLoopBackOff)
```bash
kubectl logs <pod-name> -c distributive
```

Check for:
- Missing environment variables
- MongoDB connection timeouts (wait 1-2 more minutes for MongoDB to initialize)
- Port conflicts

**Fix:** Delete and re-apply:
```bash
kubectl delete -f k8s/
kubectl apply -f k8s/
```

#### MongoDB connection refused
```bash
kubectl logs <pod-name> -c mongo
kubectl exec -it <pod-name> -c mongo -- mongosh
```

✅ **Fix:** Wait 30-60 seconds for MongoDB to fully initialize, then restart the app:
```bash
kubectl rollout restart deployment/distributive-deployment
```

### Step 7: View Application Logs

#### Streamlit app logs
```bash
kubectl logs <pod-name> -c distributive -f
```

#### MongoDB logs
```bash
kubectl logs <pod-name> -c mongo -f
```

#### Get detailed pod information
```bash
kubectl describe pod <pod-name>
```

### Step 8: Test MongoDB Connection from Inside Pod

```bash
kubectl exec -it <pod-name> -c distributive -- python /app/scripts/test_mongo.py
```

Or run the test script locally:
```bash
python scripts/test_mongo.py
```

### Step 9: Open the Application

#### Automatic (recommended)
```bash
minikube service distributive-service
```

This opens your browser automatically to the Streamlit app.

#### Manual
Get the Minikube IP and port:
```bash
minikube service distributive-service --url
```

Output example: `http://192.168.49.2:30007`

Copy the URL into your browser.

### Step 10: Test the Application

1. **Navigate to the Streamlit app** (from Step 9)
2. **Interact with the app** - Verify that:
   - The app loads without errors
   - UI renders correctly
   - Any data operations work (if applicable)
   - MongoDB integration is functional

### Step 11: Scale or Restart Deployments

#### Increase replicas
```bash
kubectl scale deployment distributive-deployment --replicas=4
```

#### Restart deployment (rolling update)
```bash
kubectl rollout restart deployment/distributive-deployment
```

#### View rollout status
```bash
kubectl rollout status deployment/distributive-deployment
```

## Cleanup

### Delete all Kubernetes resources
```bash
kubectl delete -f k8s/
```

### Stop Minikube (keep the VM)
```bash
minikube stop
```

### Delete Minikube cluster entirely
```bash
minikube delete
```

## Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|----------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `distributive_db` | Database name |
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit port |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Bind address |
| `STREAMLIT_LOGGER_LEVEL` | `info` | Log level |

## Performance Tuning

### For slower machines:
```bash
minikube start --driver=docker --memory=2048 --cpus=1
```

### For better performance:
```bash
minikube start --driver=docker --memory=8192 --cpus=4
```

## Common Commands Reference

```bash
# View all Kubernetes resources
kubectl get all

# Watch pods in real-time
kubectl get pods -w

# SSH into Minikube VM (for advanced debugging)
minikube ssh

# View Minikube dashboard
minikube dashboard

# Check Minikube status
minikube status

# View events
kubectl get events
```

## Next Steps

1. ✅ Application is running in Kubernetes
2. 📊 View logs and verify functionality
3. 🔄 Scale up/down replicas as needed
4. 🚀 Push to Docker Hub/GCR for production deployment
5. 📝 Update ingress rules for production URLs

## Support

For issues:
1. Check logs: `kubectl logs <pod-name> -c <container-name>`
2. Describe pod: `kubectl describe pod <pod-name>`
3. Check events: `kubectl get events`
4. Verify Docker image: `docker images | grep distributive`
