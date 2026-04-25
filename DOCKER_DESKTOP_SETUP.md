# 🐳 Docker Desktop Kubernetes Setup & Configuration Guide

This guide walks you through setting up and running the Distributive application using **Docker Desktop's built-in Kubernetes** instead of Minikube.

---

## 📋 Prerequisites

- **Docker Desktop** installed (Windows, macOS, or Linux)
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Git** installed for cloning the repository
- **kubectl** (included with Docker Desktop)
- **4GB+ RAM** allocated to Docker Desktop
- **2+ CPU cores** allocated to Docker Desktop

---

## ✅ Part 1: Install and Enable Kubernetes in Docker Desktop

### Step 1: Install Docker Desktop

1. **Download** Docker Desktop for your OS:
   - [Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
   - [macOS](https://desktop.docker.com/mac/main/amd64/Docker.dmg)
   - [Linux](https://docs.docker.com/desktop/install/linux-install/)

2. **Install** and complete the setup wizard
3. **Launch** Docker Desktop application
4. **Wait** 2-3 minutes for Docker daemon to start completely

### Step 2: Enable Kubernetes in Docker Desktop

#### Windows/macOS:
1. Click the **Docker icon** in the system tray (top-right corner)
2. Select **Preferences** or **Settings**
3. Go to **Kubernetes** tab
4. Check the box: **✓ Enable Kubernetes**
5. Select **Docker Desktop** as the orchestrator
6. Click **Apply & Restart**
7. **Wait 3-5 minutes** for Kubernetes to initialize

#### Linux:
Kubernetes is **not available** on Linux Docker Desktop. Use **Minikube** instead (see `MINIKUBE_SETUP.md`)

### Step 3: Verify Kubernetes is Running

Open a terminal/PowerShell and run:

```bash
kubectl version --client
```

**Expected output:**
```
Client Version: v1.28.x
Kustomize Version: v5.x.x
```

If you get an error, Kubernetes is still initializing. Wait a few more minutes.

```bash
kubectl get nodes
```

**Expected output:**
```
NAME             STATUS   ROLES           AGE     VERSION
docker-desktop   Ready    control-plane   2m      v1.28.x
```

✅ If you see `docker-desktop` with `Ready` status, Kubernetes is successfully enabled!

---

## 🚀 Part 2: Deploy Application with Docker Desktop Kubernetes

### Step 1: Clone or Navigate to Your Project

```bash
# If you haven't cloned yet
git clone https://github.com/ramya883/distributive.git
cd distributive

# Or if you already have it
cd path/to/distributive
```

### Step 2: Build Docker Image

```bash
# Build the image
docker build -t distributive-app:latest .
```

**Expected output:**
```
Sending build context to Docker daemon  ...
Step 1/XX FROM python:3.12-slim
...
Successfully tagged distributive-app:latest
```

✅ **Verify the image was created:**
```bash
docker images | grep distributive
```

### Step 3: Verify kubectl is Using Docker Desktop

```bash
kubectl config current-context
```

**Expected output:**
```
docker-desktop
```

If you see a different context (like `minikube`), switch to Docker Desktop:

```bash
kubectl config use-context docker-desktop
```

### Step 4: Create Kubernetes Namespace (Optional but Recommended)

```bash
kubectl create namespace distributive-app
```

### Step 5: Deploy to Kubernetes

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

**Expected output:**
```
deployment.apps/distributive-deployment created
service/distributive-service created
service/mongo-service created
```

### Step 6: Verify Deployment

#### Check Pods Status
```bash
kubectl get pods
```

**Wait 30-60 seconds**, then run again until you see:
```
NAME                                      READY   STATUS    RESTARTS   AGE
distributive-deployment-xxxxx-xxxxx       2/2     Running   0          45s
distributive-deployment-xxxxx-xxxxx       2/2     Running   0          40s
```

✅ Both containers must show **2/2 READY**

#### Check Services
```bash
kubectl get services
```

**Expected output:**
```
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
distributive-service    NodePort    10.x.x.x        <none>        8501:30007/TCP
mongo-service           ClusterIP   10.x.x.x        <none>        27017/TCP
kubernetes              ClusterIP   10.96.0.1       <none>        443/TCP
```

#### Check Deployments
```bash
kubectl get deployments
```

**Expected output:**
```
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
distributive-deployment     2/2     2            2           2m
```

---

## 🌐 Part 3: Access the Application

### Option 1: Using kubectl Port Forward (Recommended)

```bash
kubectl port-forward svc/distributive-service 8501:8501
```

**Expected output:**
```
Forwarding from 127.0.0.1:8501 -> 8501
Forwarding from [::1]:8501 -> 8501
Handling connection for 8501
```

Then open your browser and go to:
```
http://localhost:8501
```

### Option 2: Using NodePort Directly

Since Docker Desktop uses `localhost` for node IP:

```bash
http://localhost:30007
```

### Option 3: Using Docker Desktop Dashboard

Docker Desktop includes a dashboard to visualize deployments:

1. Click **Docker icon** → **Dashboard**
2. Navigate to **Kubernetes** section
3. View running pods and services
4. Click on services to see endpoints

---

## 🔍 Part 4: Troubleshooting

### Issue 1: Pods Stuck in "Pending" State

```bash
kubectl describe pod <pod-name>
```

**Common causes:**
- Docker Desktop doesn't have enough resources
- Image pull issues

**Fix:**
1. Go to **Docker Settings** → **Resources**
2. Increase **Memory** to **6GB+**
3. Increase **CPUs** to **4+**
4. Click **Apply**
5. Restart Docker
6. Redeploy:
   ```bash
   kubectl delete -f k8s/
   kubectl apply -f k8s/
   ```

### Issue 2: ImagePullBackOff or ErrImagePull

```bash
kubectl describe pod <pod-name>
```

**Cause:** The image doesn't exist in Docker Desktop's local registry

**Fix:**
```bash
# Rebuild the image
docker build -t distributive-app:latest .

# Check the image exists
docker images | grep distributive

# Delete the pod so it gets recreated
kubectl delete pod <pod-name>

# Kubernetes will recreate it and use the new image
```

### Issue 3: CrashLoopBackOff - App Keeps Restarting

```bash
# Check app logs
kubectl logs <pod-name> -c distributive --tail=50
```

**Common causes:**
- MongoDB not yet initialized
- Missing environment variables
- Port conflicts

**Fix:**
```bash
# Check if MongoDB is running
kubectl logs <pod-name> -c mongo --tail=20

# Wait for MongoDB to start (30-60 seconds)
kubectl wait --for=condition=ready pod -l app=distributive --timeout=120s

# Restart the deployment
kubectl rollout restart deployment/distributive-deployment
```

### Issue 4: "Connection refused" from App to MongoDB

**Cause:** MongoDB is still initializing

**Fix:**
```bash
# Check MongoDB logs
kubectl logs <pod-name> -c mongo

# Wait and then test the connection
kubectl exec -it <pod-name> -c distributive -- python scripts/test_mongo.py
```

### Issue 5: Port 8501 Already in Use

If port 8501 is already in use:

```bash
# Use a different port
kubectl port-forward svc/distributive-service 9999:8501

# Then access at http://localhost:9999
```

---

## 📊 Part 5: Monitoring and Debugging

### View All Kubernetes Resources

```bash
kubectl get all
```

### View Detailed Pod Information

```bash
kubectl describe pod <pod-name>
```

### View Real-time Pod Logs

```bash
# Streamlit app logs
kubectl logs <pod-name> -c distributive -f

# MongoDB logs
kubectl logs <pod-name> -c mongo -f

# Both containers
kubectl logs <pod-name> -f --all-containers=true
```

### Watch Pods in Real-time

```bash
kubectl get pods -w
```

Press `Ctrl+C` to exit.

### Get Pod Shell Access

```bash
# Access the Streamlit container
kubectl exec -it <pod-name> -c distributive -- /bin/bash

# Access the MongoDB container
kubectl exec -it <pod-name> -c mongo -- mongosh
```

### View Events

```bash
kubectl get events --sort-by='.lastTimestamp'
```

---

## 🛠️ Part 6: Common Operations

### Scale Replicas

```bash
# Scale to 4 replicas
kubectl scale deployment distributive-deployment --replicas=4

# Check status
kubectl get pods
```

### Restart Deployment

```bash
kubectl rollout restart deployment/distributive-deployment
```

### Check Rollout Status

```bash
kubectl rollout status deployment/distributive-deployment
```

### Update Deployment Image

If you rebuild the image:

```bash
# Delete old pods so they get recreated with new image
kubectl delete pods -l app=distributive
```

### View Pod Resource Usage

```bash
kubectl top nodes
kubectl top pods
```

### Access MongoDB from Your Machine

```bash
# Port forward MongoDB
kubectl port-forward svc/mongo-service 27017:27017

# In another terminal, connect with mongosh
mongosh mongodb://localhost:27017
```

---

## 🧪 Part 7: Testing the Application

### Test MongoDB Connectivity

```bash
# Run test from your machine
python scripts/test_mongo.py

# Or run inside the pod
kubectl exec -it <pod-name> -c distributive -- python scripts/test_mongo.py
```

### Test Streamlit Health Endpoint

```bash
# Using curl from your machine
curl http://localhost:8501/_stcore/health

# Or using port-forward
kubectl port-forward svc/distributive-service 8501:8501
curl http://localhost:8501/_stcore/health
```

### Test MongoDB Connection from Inside Pod

```bash
kubectl exec -it <pod-name> -c mongo -- mongosh
```

Inside mongosh:
```javascript
db.adminCommand('ping')
db.test_collection.insertOne({test: true})
db.test_collection.find()
```

---

## 🧹 Part 8: Cleanup & Removal

### Delete Application Only

```bash
kubectl delete -f k8s/
```

**Expected output:**
```
deployment.apps "distributive-deployment" deleted
service "distributive-service" deleted
service "mongo-service" deleted
```

### Delete Namespace (if created)

```bash
kubectl delete namespace distributive-app
```

### Remove Docker Image

```bash
docker rmi distributive-app:latest
```

### Disable Kubernetes in Docker Desktop

1. Click **Docker icon** → **Preferences/Settings**
2. Go to **Kubernetes** tab
3. Uncheck **✓ Enable Kubernetes**
4. Click **Apply**

---

## 📈 Advanced: Using Docker Desktop Dashboard

Docker Desktop includes a visual dashboard:

```bash
# Docker Desktop automatically opens it, or use:
open http://localhost:3000  # macOS
# or navigate to Docker app → Dashboard
```

**Features:**
- 📊 View pods, deployments, services
- 📝 View logs in real-time
- 🔄 Restart containers
- 📉 View resource usage
- 🔍 Debug containers

---

## 🔐 Part 9: Production Considerations

Before deploying to production, consider:

### 1. Use Private Registry

Instead of building locally, push to Docker Hub or private registry:

```bash
# Tag image
docker tag distributive-app:latest yourusername/distributive-app:v1.0

# Push to Docker Hub
docker login
docker push yourusername/distributive-app:v1.0

# Update k8s/deployment.yaml
# image: yourusername/distributive-app:v1.0
# imagePullPolicy: IfNotPresent
```

### 2. Use PersistentVolumes for MongoDB

Replace `emptyDir` in deployment.yaml:

```yaml
volumes:
  - name: mongo-data
    persistentVolumeClaim:
      claimName: mongo-pvc
```

Create PVC:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 3. Enable Ingress

Replace NodePort with Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: distributive-ingress
spec:
  rules:
  - host: distributive.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: distributive-service
            port:
              number: 8501
```

### 4. Enable Network Policies

Restrict traffic between pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: distributive-netpolicy
spec:
  podSelector:
    matchLabels:
      app: distributive
  policyTypes:
  - Ingress
  - Egress
```

### 5. Use Secrets for Credentials

```bash
kubectl create secret generic mongo-credentials \
  --from-literal=username=admin \
  --from-literal=password=secretpassword
```

Then reference in deployment:
```yaml
env:
  - name: MONGO_USERNAME
    valueFrom:
      secretKeyRef:
        name: mongo-credentials
        key: username
```

---

## 📚 Quick Reference Commands

| Task | Command |
|------|---------|
| Build image | `docker build -t distributive-app:latest .` |
| Deploy | `kubectl apply -f k8s/` |
| Check status | `kubectl get pods` |
| View logs | `kubectl logs <pod-name> -c <container>` |
| Port forward | `kubectl port-forward svc/distributive-service 8501:8501` |
| Scale replicas | `kubectl scale deployment distributive-deployment --replicas=4` |
| Restart deployment | `kubectl rollout restart deployment/distributive-deployment` |
| Delete deployment | `kubectl delete -f k8s/` |
| Get shell access | `kubectl exec -it <pod-name> -c <container> -- /bin/bash` |
| View resources | `kubectl get all` |
| Describe pod | `kubectl describe pod <pod-name>` |
| Delete pod | `kubectl delete pod <pod-name>` |
| Watch pods | `kubectl get pods -w` |

---

## 🎯 Complete Workflow Summary

```
1. Install Docker Desktop
   ↓
2. Enable Kubernetes in Docker Desktop settings
   ↓
3. Build Docker image: docker build -t distributive-app:latest .
   ↓
4. Apply Kubernetes manifests: kubectl apply -f k8s/
   ↓
5. Wait for pods to be ready: kubectl get pods
   ↓
6. Port forward: kubectl port-forward svc/distributive-service 8501:8501
   ↓
7. Open browser: http://localhost:8501
   ↓
8. Interact with the application
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `kubectl logs <pod-name> -c <container> --tail=50`
2. **Describe pod**: `kubectl describe pod <pod-name>`
3. **Check events**: `kubectl get events --sort-by='.lastTimestamp'`
4. **Verify image**: `docker images | grep distributive`
5. **Check Docker Desktop logs**: Docker icon → Troubleshoot

---

## 📞 Contact & Support

For detailed troubleshooting, see:
- `README.md` - Project overview
- `MINIKUBE_SETUP.md` - Minikube alternative
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Desktop Documentation](https://docs.docker.com/desktop/)

---

**Last Updated**: April 25, 2026
