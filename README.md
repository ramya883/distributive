# 🚀 Distributive - AI & Cloud Project

A containerized Streamlit application with MongoDB integration, ready for local development with Docker Compose and production deployment with Kubernetes.

## 📋 Features

- **Streamlit Frontend**: Interactive web interface for AI and cloud applications
- **MongoDB Database**: NoSQL data persistence with sidecar pattern
- **Docker Support**: Multi-stage Dockerfile with optimized layers
- **Kubernetes Ready**: Complete K8s manifests for Minikube deployment
- **Health Checks**: Built-in liveness and readiness probes
- **MongoDB Integration**: CRUD operations with Python/PyMongo
- **Development Tools**: Test scripts and troubleshooting guides

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      Streamlit Application          │
│  (Port 8501)                        │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │   Pod/Container │
       │  ┌───────────────────┐
       │  │ Streamlit (8501)  │
       │  └─────────┬─────────┘
       │            │
       │  ┌─────────▼─────────┐
       │  │  MongoDB (27017)  │
       │  └───────────────────┘
       └─────────────────────┘
```

## 🚀 Quick Start

### Option 1: Local Development (Docker Compose)

```bash
# Start the application
docker-compose up

# Open browser to http://localhost:8501
```

### Option 2: Kubernetes Deployment (Minikube)

```bash
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Configure Docker environment
eval $(minikube docker-env)  # macOS/Linux
minikube docker-env | Invoke-Expression  # Windows PowerShell

# Build image
docker build -t distributive-app:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Open application
minikube service distributive-service
```

See [MINIKUBE_SETUP.md](MINIKUBE_SETUP.md) for detailed instructions.

## 📦 Project Structure

```
distributive/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages for Streamlit
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Local development setup
├── .env.example              # Environment variables template
├── .dockerignore              # Docker build ignore rules
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── k8s/
│   ├── deployment.yaml      # Kubernetes deployment (2 replicas)
│   └── service.yaml         # Kubernetes services (NodePort + ClusterIP)
├── scripts/
│   └── test_mongo.py        # MongoDB connectivity test
├── MINIKUBE_SETUP.md        # Kubernetes deployment guide
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Key variables:
- `MONGO_URI`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGO_DB_NAME`: Database name (default: `distributive_db`)
- `STREAMLIT_SERVER_PORT`: Streamlit port (default: `8501`)
- `STREAMLIT_SERVER_ADDRESS`: Bind address (default: `0.0.0.0`)

### MongoDB

MongoDB runs as a sidecar container alongside the Streamlit app:
- **In Docker Compose**: Service named `mongo`
- **In Kubernetes**: Same pod as the app container
- **Connection**: `mongodb://mongo:27017` (Docker) or `mongodb://localhost:27017` (K8s)

## 🧪 Testing

### Test MongoDB Connection

```bash
# From your machine
python scripts/test_mongo.py

# From inside a Kubernetes pod
kubectl exec -it <pod-name> -c distributive -- python scripts/test_mongo.py
```

### Docker Compose Testing

```bash
# Start services
docker-compose up

# In another terminal, test MongoDB
docker exec -it mongo mongosh

# Inside mongosh:
> db.adminCommand('ping')
```

## 🐳 Docker Commands

```bash
# Build image
docker build -t distributive-app:latest .

# Run container (local MongoDB)
docker run -p 8501:8501 -e MONGO_URI=mongodb://host.docker.internal:27017 distributive-app:latest

# Run with Docker Compose
docker-compose up
docker-compose down  # Stop services
```

## ☸️ Kubernetes Commands

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services
kubectl get deployments

# View logs
kubectl logs <pod-name> -c distributive
kubectl logs <pod-name> -c mongo

# Port forward (alternative to NodePort)
kubectl port-forward svc/distributive-service 8501:8501

# Delete resources
kubectl delete -f k8s/
```

## 🔍 Troubleshooting

### "Connection refused" from app to MongoDB

1. Check if MongoDB pod/container is running:
   ```bash
   docker-compose ps  # or
   kubectl get pods
   ```
2. Wait 30-60 seconds for MongoDB to initialize
3. Check MongoDB logs:
   ```bash
   docker-compose logs mongo  # or
   kubectl logs <pod-name> -c mongo
   ```

### Streamlit app won't start

1. Check application logs:
   ```bash
   docker-compose logs app  # or
   kubectl logs <pod-name> -c distributive
   ```
2. Verify `requirements.txt` is installed:
   ```bash
   docker build -t distributive-app:latest . --no-cache
   ```
3. Check environment variables are set correctly

### Image not found in Minikube

1. Ensure you configured Docker environment:
   ```bash
   eval $(minikube docker-env)  # macOS/Linux
   minikube docker-env | Invoke-Expression  # Windows PowerShell
   ```
2. Rebuild the image:
   ```bash
   docker build -t distributive-app:latest .
   ```
3. Use `imagePullPolicy: Never` (already set in deployment.yaml)

## 📊 Health Endpoints

- **Streamlit Health**: `http://localhost:8501/_stcore/health`
- **MongoDB Health**: Test via `mongosh` or Python script

## 🔐 Security Considerations

For production deployment:

1. **Secrets Management**: Use Kubernetes Secrets for credentials
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: mongo-credentials
   type: Opaque
   data:
     username: <base64-encoded>
     password: <base64-encoded>
   ```

2. **Network Policies**: Restrict pod-to-pod communication

3. **RBAC**: Implement Role-Based Access Control

4. **Image Registry**: Push to private registry (Docker Hub, GCR, ECR)

5. **MongoDB Authentication**: Enable auth in production

## 📈 Scaling

### Scale replicas in Kubernetes

```bash
# Scale to 4 replicas
kubectl scale deployment distributive-deployment --replicas=4

# Or edit deployment
kubectl edit deployment distributive-deployment
```

### Performance tuning

**Docker Compose resource limits**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Kubernetes resource requests/limits** (already in k8s/deployment.yaml)

## 🚢 Production Deployment

For production, follow these steps:

1. **Update image registry** in `k8s/deployment.yaml`:
   ```yaml
   image: docker.io/yourusername/distributive-app:v1.0
   imagePullPolicy: IfNotPresent
   ```

2. **Push to registry**:
   ```bash
   docker tag distributive-app:latest docker.io/yourusername/distributive-app:v1.0
   docker push docker.io/yourusername/distributive-app:v1.0
   ```

3. **Enable ingress** for external traffic

4. **Use PersistentVolumes** for MongoDB data (replace emptyDir)

5. **Add resource quotas and network policies**

6. **Setup monitoring** with Prometheus/Grafana

## 📚 Additional Resources

- [Streamlit Docs](https://docs.streamlit.io/)
- [MongoDB PyMongo Docs](https://pymongo.readthedocs.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Setup](MINIKUBE_SETUP.md)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 📝 License

This project is open source and available under the MIT License.

## 👤 Contributors

Ramya (@ramya883)

---

**Last Updated**: April 25, 2026
