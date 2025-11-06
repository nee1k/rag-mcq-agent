# Kubernetes Deployment Guide

## Prerequisites

1. **Kubernetes cluster** running (options):
   - Minikube: `minikube start`
   - Kind: `kind create cluster`
   - Cloud cluster (GKE, EKS, AKS)
   - Local Docker Desktop with Kubernetes enabled

2. **kubectl** installed and configured
   - Install: `sudo snap install kubectl` (Linux)
   - Verify: `kubectl cluster-info`

3. **Docker** installed (for building images)

## Quick Start

### Option 1: Automated Deployment Script

```bash
cd k8s
./deploy.sh
```

The script will:
- Create namespace
- Create ConfigMap from testbench.csv
- Prompt for OpenAI API key secret creation
- Build Docker image
- Load image into cluster (if minikube/kind)
- Deploy the Job

### Option 2: Manual Deployment

#### Step 1: Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

#### Step 2: Create ConfigMap
```bash
kubectl create configmap hip-agent-config \
  --from-file=testbench.csv=testbench.csv \
  -n hip-agent
```

#### Step 3: Create Secret for OpenAI API Key
```bash
# From environment variable
export OPENAI_API_KEY='your-key-here'
kubectl create secret generic openai-api-key \
  --from-literal=api-key=$OPENAI_API_KEY \
  -n hip-agent

# OR from .env file (if it exists)
source .env
kubectl create secret generic openai-api-key \
  --from-literal=api-key=$OPENAI_API_KEY \
  -n hip-agent
```

#### Step 4: Build Docker Image
```bash
docker build -t hip-agent:latest .
```

#### Step 5: Load Image into Cluster

**For Minikube:**
```bash
minikube image load hip-agent:latest
```

**For Kind:**
```bash
kind load docker-image hip-agent:latest
```

**For Cloud Clusters:**
Push to a container registry instead:
```bash
docker tag hip-agent:latest your-registry/hip-agent:latest
docker push your-registry/hip-agent:latest
# Then update image in job.yaml to use the registry URL
```

#### Step 6: Deploy Job
```bash
cd k8s
kubectl apply -f k8s/job.yaml
```

#### Step 7: View Results
```bash
# Watch logs
kubectl logs -f job/hip-agent-testbench -n hip-agent

# Check job status
kubectl get jobs -n hip-agent

# View job details
kubectl describe job hip-agent-testbench -n hip-agent
```

## Troubleshooting

### Image Pull Errors
- For local clusters (minikube/kind): Make sure you loaded the image
- For cloud clusters: Ensure image is pushed to registry and imagePullPolicy is correct

### Secret Not Found
```bash
# Check if secret exists
kubectl get secret openai-api-key -n hip-agent

# If not, create it (see Step 3 above)
```

### ConfigMap Not Found
```bash
# Check if ConfigMap exists
kubectl get configmap hip-agent-config -n hip-agent

# Recreate if needed
kubectl create configmap hip-agent-config \
  --from-file=testbench.csv=../testbench.csv \
  -n hip-agent
```

### View Pod Logs
```bash
# Get pod name
kubectl get pods -n hip-agent

# View logs
kubectl logs <pod-name> -n hip-agent
```

### Delete Resources
```bash
# Delete job
kubectl delete job hip-agent-testbench -n hip-agent

# Delete everything in namespace
kubectl delete namespace hip-agent
```

## Current Status

- [x] Basic Job-based deployment
- [x] Dockerfile created
- [x] ConfigMap mounting working
- [x] Secret management for API key

## Resources

The deployment uses minimal Kubernetes resources:
- **Namespace**: `hip-agent` - isolates resources
- **ConfigMap**: `hip-agent-config` - stores testbench.csv
- **Secret**: `openai-api-key` - stores OpenAI API key securely
- **Job**: `hip-agent-testbench` - runs the testbench once

