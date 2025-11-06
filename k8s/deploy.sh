#!/bin/bash
# Deployment script for HIP Agent in Kubernetes

set -e

echo "🚀 Deploying HIP Agent to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your cluster connection."
    exit 1
fi

# Step 1: Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Step 2: Create ConfigMap from testbench.csv
echo "📋 Creating ConfigMap from testbench.csv..."
kubectl create configmap hip-agent-config \
  --from-file=testbench.csv=../testbench.csv \
  -n hip-agent \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Check if secret exists, if not prompt user
echo "🔐 Checking for OpenAI API key secret..."
if ! kubectl get secret openai-api-key -n hip-agent &> /dev/null; then
    echo "⚠️  Secret 'openai-api-key' not found."
    echo "Please create it using one of these methods:"
    echo ""
    echo "Method 1: From environment variable"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  kubectl create secret generic openai-api-key \\"
    echo "    --from-literal=api-key=\$OPENAI_API_KEY -n hip-agent"
    echo ""
    echo "Method 2: From .env file (if OPENAI_API_KEY is set)"
    if [ -f ../.env ]; then
        source ../.env
        if [ -n "$OPENAI_API_KEY" ]; then
            echo "  Found OPENAI_API_KEY in .env file"
            read -p "Create secret from .env file? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kubectl create secret generic openai-api-key \
                  --from-literal=api-key="$OPENAI_API_KEY" \
                  -n hip-agent
                echo "✅ Secret created from .env file"
            fi
        fi
    fi
    echo ""
    echo "If you've created the secret manually, press Enter to continue..."
    read
fi

# Step 4: Build Docker image
echo "🐳 Building Docker image..."
cd ..
docker build -t hip-agent:latest .

# Step 5: Load image into cluster (for local clusters)
# Detect cluster type and load image accordingly
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "📤 Loading image into minikube..."
    minikube image load hip-agent:latest
elif command -v kind &> /dev/null && kind get clusters &> /dev/null; then
    echo "📤 Loading image into kind..."
    kind load docker-image hip-agent:latest
fi

cd k8s

# Step 6: Deploy Job
echo "⚙️  Deploying testbench Job..."
kubectl apply -f job.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To view logs:"
echo "  kubectl logs -f job/hip-agent-testbench -n hip-agent"
echo ""
echo "To check job status:"
echo "  kubectl get jobs -n hip-agent"
echo ""
echo "To delete the job:"
echo "  kubectl delete job hip-agent-testbench -n hip-agent"

