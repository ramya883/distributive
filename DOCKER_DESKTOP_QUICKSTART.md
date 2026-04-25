# 🐳 Docker Desktop Quick Start Guide

Complete step-by-step guide to run the Distributive application on Docker Desktop with Kubernetes support.

---

## 📋 Prerequisites

Before starting, ensure you have:

1. **Docker Desktop installed** ([Download](https://www.docker.com/products/docker-desktop))
   - Windows 10/11 Pro, Enterprise, or Education
   - macOS 11+ (Intel or Apple Silicon)
   - Linux with Docker installed

2. **Verify Docker Desktop is running**
   ```bash
   docker --version
   docker ps  # Should show no errors
   ```

3. **Enable Kubernetes in Docker Desktop**
   - See **Step 1** below

---

## 🎯 Step 1: Enable Kubernetes in Docker Desktop

### macOS / Windows:

1. Click **Docker icon** in taskbar → **Settings** (or **Preferences** on macOS)
2. Go to **Kubernetes** tab
3. Check **✓ Enable Kubernetes**
4. Click **Apply & Restart**
5. Wait 2-3 minutes for Kubernetes to start (you'll see a spinning whale icon)
6. Verify: Look for a green dot next to "Kubernetes is running"

### Verify Kubernetes is Running:

```bash
kubectl cluster-info
kubectl get nodes
```

**Expected output:**
```
Kubernetes control plane is running at https://127.0.0.1:6443
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   2m    v1.28.x
```

✅ **If you see this, Kubernetes is ready!**

---

## 📂 Step 2: Clone & Navigate to Project

```bash
# Navigate to your project directory
cd /path/to/distributive

# Verify files exist
ls -la
# You should see: app.py, Dockerfile, docker-compose.yml, k8s/, etc.
```

---

## 🚀 Step 3: Option A - Run with Docker Compose (EASIEST)

Docker Compose automatically manages containers and networking.

### 3A.1: Build the Docker Image

```bash
docker-compose build
```

**Expected output:**
```
Building app
[+] Building 45.2s (12/12) FINISHED
...
Successfully tagged distributive-app:latest
```

### 3A.2: Start Services

```bash
docker-compose up
```

**Expected output:**
```
Creating mongo    ... done
Creating distributive-app ... done
Attaching to mongo, distributive-app
mongo    | 2026-04-25T14:30:00.123+0000 I NETWORK  [initandlisten] listening on all available network interfaces
app      | 2026-04-25 14:30:05.123 INFO streamlit.Server
app      | You can now view your app in your browser.
app      | Local URL: http://localhost:8501
```

### 3A.3: Access the Application

🌐 **Open your browser to: http://localhost:8501**

You should see the Distributive dashboard!

### 3A.4: Test MongoDB Connection

In another terminal:
```bash
docker-compose exec app python scripts/test_mongo.py
```

**Expected output:**
```
✅ MongoDB connection successful!
✅ Test document inserted: 65aec3a1c2d1a2b3c4d5e6f7
✅ Test document retrieved: {...}
✅ All tests passed!
```

### 3A.5: Stop Services

```bash
# Stop all containers (keep data)
docker-compose stop

# Or remove everything (cleanup)
docker-compose down
```

---

## ☸️ Step 4: Option B - Run with Kubernetes (ADVANCED)

If you want to use Kubernetes instead of Docker Compose:

### 4B.1: Build Docker Image

```bash
# Build the image
docker build -t distributive-app:latest .

# Verify the image
docker images | grep distributive
```

**Expected output:**
```
REPOSITORY           TAG       IMAGE ID       CREATED        SIZE
distributive-app     latest    abc123def456   2 minutes ago   1.2GB
```

### 4B.2: Deploy to Kubernetes

```bash
# Apply the manifests
kubectl apply -f k8s/

# Verify deployment
kubectl get pods
```

**Expected output (wait 30-60 seconds):**
```
NAME                                      READY   STATUS    RESTARTS   AGE
distributive-deployment-abc123def-xyz00   2/2     Running   0          45s
distributive-deployment-abc123def-xyz11   2/2     Running   0          40s
```

✅ **Both containers (app + mongo) should show 2/2 READY**

### 4B.3: Check Services

```bash
kubectl get services
```

**Expected output:**
```
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
distributive-service    NodePort    10.96.x.x       <none>        8501:30007/TCP      2m
mongo-service           ClusterIP   10.96.x.x       <none>        27017/TCP           2m
kubernetes              ClusterIP   10.96.0.1       <none>        443/TCP             15m
```

### 4B.4: Access the Application

Find the service URL:
```bash
kubectl get service distributive-service
```

🌐 **Open browser to: http://localhost:30007**

Or use port forwarding:
```bash
kubectl port-forward svc/distributive-service 8501:8501
# Then visit: http://localhost:8501
```

### 4B.5: View Logs

```bash
# Get pod name
kubectl get pods

# View Streamlit app logs
kubectl logs <pod-name> -c distributive -f

# View MongoDB logs
kubectl logs <pod-name> -c mongo -f

# Example:
# kubectl logs distributive-deployment-abc123def-xyz00 -c distributive -f
```

### 4B.6: Test MongoDB from Kubernetes

```bash
# Get pod name
POD=$(kubectl get pods -o jsonpath='{.items[0].metadata.name}')

# Run test script
kubectl exec -it $POD -c distributive -- python scripts/test_mongo.py
```

### 4B.7: Scale the Deployment

```bash
# Scale to 4 replicas
kubectl scale deployment distributive-deployment --replicas=4

# Verify
kubectl get pods
# You should see 4 pods now, each with 2/2 containers
```

### 4B.8: Clean Up Kubernetes

```bash
# Delete all resources
kubectl delete -f k8s/

# Verify deletion
kubectl get pods  # Should show nothing
```

---

## 🎯 Comparison: Docker Compose vs Kubernetes

| Feature | Docker Compose | Kubernetes |
|---------|---|---|
| **Simplicity** | ✅ Simple (1 command) | ⚠️ More complex |
| **Development** | ✅ Perfect for local dev | ✅ Production-like |
| **Learning Curve** | ✅ Easy | ⚠️ Steeper |
| **Scaling** | ⚠️ Manual | ✅ Automatic |
| **Health Checks** | ✅ Basic | ✅ Advanced |
| **Resource Limits** | ✅ Supported | ✅ Built-in |
| **Start Time** | ✅ Fast (5-10s) | ⚠️ Slower (30-60s) |

**Recommendation**: Use **Docker Compose** for quick testing, **Kubernetes** for learning and production simulation.

---

## 🔥 Common Tasks

### Check Application Logs

**Docker Compose:**
```bash
docker-compose logs -f app
docker-compose logs -f mongo
```

**Kubernetes:**
```bash
kubectl logs -f deployment/distributive-deployment -c distributive
kubectl logs -f deployment/distributive-deployment -c mongo
```

### Access MongoDB CLI

**Docker Compose:**
```bash
docker-compose exec mongo mongosh
```

**Kubernetes:**
```bash
POD=$(kubectl get pods -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -c mongo -- mongosh
```

### Check Resource Usage

**Docker Compose:**
```bash
docker stats
```

**Kubernetes:**
```bash
kubectl top pods
kubectl top nodes
```

### Restart Services

**Docker Compose:**
```bash
docker-compose restart app
docker-compose restart mongo
```

**Kubernetes:**
```bash
kubectl rollout restart deployment/distributive-deployment
```

### View All Running Containers/Pods

**Docker Compose:**
```bash
docker ps
docker ps -a  # Including stopped containers
```

**Kubernetes:**
```bash
kubectl get all
kubectl describe pod <pod-name>
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" error in app

**Cause**: MongoDB not ready yet
**Solution**: 
```bash
# Docker Compose
docker-compose logs mongo

# Kubernetes
kubectl logs <pod-name> -c mongo

# Wait 30-60 seconds and try again
```

### Issue: Kubernetes shows "ImagePullBackOff"

**Cause**: Image not found locally
**Solution**:
```bash
# Build the image first
docker build -t distributive-app:latest .

# Verify it exists
docker images | grep distributive

# Then deploy
kubectl apply -f k8s/
```

### Issue: Port 8501 already in use

**Cause**: Another application using the port
**Solution**:

**Docker Compose**:
```bash
# Change port in docker-compose.yml
# Change: 8501:8501
# To:     8502:8501
# Then: docker-compose up
```

**Kubernetes**:
```bash
# Use port forwarding to a different port
kubectl port-forward svc/distributive-service 8502:8501
# Visit: http://localhost:8502
```

### Issue: Docker Desktop won't start Kubernetes

**Solution**:
1. Go to Docker Desktop **Settings** → **Reset**
2. Click **Reset Kubernetes Cluster** or **Reset Docker to Factory Defaults**
3. Wait for restart
4. Re-enable Kubernetes (Step 1)
5. Verify with `kubectl cluster-info`

### Issue: Out of disk space

**Solution**:
```bash
# Docker Compose
docker-compose down
docker system prune -a  # Remove unused images/containers

# Kubernetes
kubectl delete -f k8s/
docker system prune -a
```

---

## 📊 Health Checks

### Verify Everything is Working

```bash
# 1. Check Docker
docker --version
docker ps

# 2. Check Kubernetes (if using K8s)
kubectl cluster-info
kubectl get nodes

# 3. Check Application Health
curl http://localhost:8501/_stcore/health

# 4. Check MongoDB
# Docker Compose
docker-compose exec mongo mongosh --eval "db.adminCommand('ping')"

# Kubernetes
POD=$(kubectl get pods -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -c mongo -- mongosh --eval "db.adminCommand('ping')"
```

---

## 🎓 Learning Resources

### Understanding Docker
- [Docker Official Tutorial](https://www.docker.com/101-app/)
- [Docker Compose Guide](https://docs.docker.com/compose/gettingstarted/)

### Understanding Kubernetes
- [Kubernetes Official Tutorial](https://kubernetes.io/docs/tutorials/)
- [Minikube vs Docker Desktop K8s](https://stackoverflow.com/questions/64413822)

### MongoDB & PyMongo
- [MongoDB PyMongo Guide](https://pymongo.readthedocs.io/)
- [MongoDB CRUD Operations](https://docs.mongodb.com/manual/crud/)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

---

## 🚀 Next Steps

### After Testing Locally

1. **Deploy to Cloud** (AWS, GCP, Azure)
   - Push image to Docker Hub or cloud registry
   - Use managed Kubernetes (EKS, GKE, AKS)
   - Follow cloud provider's deployment guide

2. **Setup CI/CD Pipeline**
   - Use GitHub Actions
   - Automated testing and deployment

3. **Production Hardening**
   - Add MongoDB authentication
   - Setup persistent volumes for data
   - Add monitoring (Prometheus, Grafana)
   - Setup logging (ELK, Datadog)
   - Configure ingress for HTTP routing

4. **Scaling**
   - Horizontal pod autoscaling
   - Load balancing
   - Database replication

---

## 📝 Quick Reference

### Docker Compose Commands

```bash
# Start
docker-compose up
docker-compose up -d  # Background

# Stop
docker-compose stop
docker-compose down

# Build
docker-compose build
docker-compose build --no-cache

# Logs
docker-compose logs
docker-compose logs -f app
docker-compose logs -f mongo

# Execute command
docker-compose exec app bash
docker-compose exec mongo mongosh

# Restart
docker-compose restart
docker-compose restart app
```

### Kubernetes Commands

```bash
# Deploy
kubectl apply -f k8s/
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# View
kubectl get pods
kubectl get services
kubectl get deployments
kubectl get all

# Details
kubectl describe pod <name>
kubectl describe service <name>
kubectl describe deployment <name>

# Logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>
kubectl logs -f <pod-name>

# Execute
kubectl exec -it <pod-name> -- bash
kubectl exec <pod-name> -c <container-name> -- command

# Edit
kubectl edit deployment <name>
kubectl patch service <name> -p '{"spec":{"type":"NodePort"}}'

# Delete
kubectl delete pod <name>
kubectl delete service <name>
kubectl delete deployment <name>
kubectl delete -f k8s/

# Scale
kubectl scale deployment <name> --replicas=4

# Port forward
kubectl port-forward pod/<name> 8501:8501
kubectl port-forward svc/<name> 8501:8501
```

---

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Kubernetes enabled in Docker Desktop
- [ ] Project files cloned locally
- [ ] `docker --version` works
- [ ] `kubectl cluster-info` shows running Kubernetes
- [ ] `docker build -t distributive-app:latest .` succeeds
- [ ] `docker-compose up` or `kubectl apply -f k8s/` succeeds
- [ ] Application loads at http://localhost:8501
- [ ] Can add/view data in the app
- [ ] MongoDB connection test passes
- [ ] Can view logs without errors

---

## 🎉 You're Ready!

You now have:
- ✅ Docker containers running
- ✅ Kubernetes cluster running
- ✅ Application deployed and accessible
- ✅ MongoDB integrated and working
- ✅ Health checks passing
- ✅ Understanding of Docker & Kubernetes

**Next**: Explore the app, try scaling, view logs, and test failover behavior!

---

**Questions?** Check [README.md](README.md) or [MINIKUBE_SETUP.md](MINIKUBE_SETUP.md) for more details.
