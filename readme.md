## Running the Application with Docker Compose

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Run docker compose

Use the provided docker-compose.yml file to build and start all services:

```bash
docker-compose up --build
```

### 3. Access the application

Navigate to port 5050 to access the application

```bash
http://localhost:5050
```

## Running the Application on Kubernetes

### 1. Start Your Kubernetes Cluster

For local network, start minikube

```bash
minikube start
```

### 2. Deploy Kubernetes Manifests

Kubernetes manifests are stored in the k8s/ folder. They include Deployments, Services, and a PersistentVolumeClaim for PostgreSQL.

Apply all manifests:

```bash
kubectl apply -f k8s/
```

### 3. Verify and Monitor Resources

Check that pods are running:

```bash
kubectl get pods
```

Check services:

```bash
kubectl get svc
```

### 4. Access the Application

If you're using a cloud provider with a LoadBalancer, your API gateway service will be assigned an external IP.
For local clusters (e.g., Minikube), run:

```bash
minikube service frontend-gateway
```

This opens the API Gateway in your default browser.
