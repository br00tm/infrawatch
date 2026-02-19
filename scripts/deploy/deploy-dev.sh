#!/bin/bash
# Deploy InfraWatch to local K3s (development overlay)
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

IMAGE_TAG="${IMAGE_TAG:-develop}"
REGISTRY="${REGISTRY:-localhost:5000}"

# Ensure KUBECONFIG is set
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
if ! kubectl cluster-info &>/dev/null; then
  err "Cannot reach Kubernetes API. Make sure K3s is running and KUBECONFIG is set."
fi

# ─────────────────────────────────────────────
# Start local Docker registry if not running
# ─────────────────────────────────────────────
if ! docker ps --format '{{.Names}}' | grep -q '^registry$'; then
  log "Starting local Docker registry at localhost:5000..."
  docker run -d -p 5000:5000 --restart=always --name registry registry:2
  sleep 2
  ok "Local registry started"
else
  ok "Local registry already running"
fi

# Configure K3s to allow insecure access to localhost:5000
REGISTRIES_FILE="/etc/rancher/k3s/registries.yaml"
if [[ ! -f "${REGISTRIES_FILE}" ]] || ! grep -q "localhost:5000" "${REGISTRIES_FILE}"; then
  log "Configuring K3s insecure registry for localhost:5000..."
  sudo tee "${REGISTRIES_FILE}" > /dev/null <<'EOF'
mirrors:
  "localhost:5000":
    endpoint:
      - "http://localhost:5000"
EOF
  sudo systemctl restart k3s
  log "Waiting for K3s to restart..."
  sleep 10
  until kubectl get nodes &>/dev/null; do sleep 2; done
  kubectl wait --for=condition=Ready nodes --all --timeout=60s
  ok "K3s registry configured"
fi

# ─────────────────────────────────────────────
# Build and push images
# ─────────────────────────────────────────────
log "Building and pushing images (tag: ${IMAGE_TAG})..."

docker build -t "${REGISTRY}/infrawatch/backend:${IMAGE_TAG}" ./backend
docker build -t "${REGISTRY}/infrawatch/frontend:${IMAGE_TAG}" ./frontend
docker build -t "${REGISTRY}/infrawatch/workers:${IMAGE_TAG}" ./workers

docker push "${REGISTRY}/infrawatch/backend:${IMAGE_TAG}"
docker push "${REGISTRY}/infrawatch/frontend:${IMAGE_TAG}"
docker push "${REGISTRY}/infrawatch/workers:${IMAGE_TAG}"

ok "Images built and pushed to ${REGISTRY}"

# ─────────────────────────────────────────────
# Create namespaces and secrets
# ─────────────────────────────────────────────
log "Creating namespaces..."
kubectl create namespace infrawatch      --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace infrawatch-data --dry-run=client -o yaml | kubectl apply -f -

log "Creating Kubernetes secrets..."
kubectl create secret generic backend-secrets \
  --namespace infrawatch \
  --from-literal=MONGODB_URL="mongodb://infrawatch:infrawatch123@infrawatch-mongodb-svc.infrawatch-data:27017/infrawatch?authSource=admin" \
  --from-literal=REDIS_URL="redis://redis.infrawatch-data:6379/0" \
  --from-literal=RABBITMQ_URL="amqp://infrawatch:infrawatch123@infrawatch-rabbitmq.infrawatch-data:5672/" \
  --from-literal=JWT_SECRET_KEY="dev-secret-key-$(openssl rand -hex 16)" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic workers-secrets \
  --namespace infrawatch \
  --from-literal=MONGODB_URL="mongodb://infrawatch:infrawatch123@infrawatch-mongodb-svc.infrawatch-data:27017/infrawatch?authSource=admin" \
  --from-literal=REDIS_URL="redis://redis.infrawatch-data:6379/0" \
  --from-literal=CELERY_BROKER_URL="redis://redis.infrawatch-data:6379/1" \
  --from-literal=CELERY_RESULT_BACKEND="redis://redis.infrawatch-data:6379/2" \
  --dry-run=client -o yaml | kubectl apply -f -

ok "Secrets created"

# ─────────────────────────────────────────────
# Apply manifests
# ─────────────────────────────────────────────
# Apply base first (Namespaces, NetworkPolicies, etc.) WITHOUT the namespace transformer
# to avoid kustomize renaming Namespace resources themselves.
log "Applying base manifests (namespaces, policies)..."
kubectl apply -f infrastructure/kubernetes/base/namespace.yaml
for f in resource-quotas.yaml priority-classes.yaml network-policies.yaml; do
  [[ -f "infrastructure/kubernetes/base/${f}" ]] && kubectl apply -f "infrastructure/kubernetes/base/${f}"
done

log "Applying Kubernetes app manifests (development overlay)..."
kubectl apply -k infrastructure/kubernetes/overlays/development/
ok "Manifests applied"

log "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend  -n infrawatch --timeout=180s
kubectl rollout status deployment/frontend -n infrawatch --timeout=180s
kubectl rollout status deployment/worker   -n infrawatch --timeout=180s
ok "All deployments ready"

echo ""
echo -e "${GREEN}=========================================="
echo "  Development deployment complete!"
echo "==========================================${NC}"
echo ""
kubectl get pods -n infrawatch
echo ""
echo "Port-forward to access locally:"
echo "  kubectl port-forward -n infrawatch svc/frontend 3000:80  &"
echo "  kubectl port-forward -n infrawatch svc/backend  8000:8000 &"
echo ""
echo "Then open: http://localhost:3000"
