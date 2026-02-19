#!/bin/bash
# Install K3s (lightweight Kubernetes) for local development/testing
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

K3S_VERSION="${K3S_VERSION:-v1.29.0+k3s1}"

log "Installing K3s ${K3S_VERSION}..."

if command -v k3s &>/dev/null; then
  warn "K3s is already installed: $(k3s --version | head -1)"
  read -rp "Reinstall? [y/N] " ans
  [[ "${ans,,}" != "y" ]] && exit 0
fi

# Install K3s with specific options
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="${K3S_VERSION}" sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --disable servicelb \
  --kube-apiserver-arg feature-gates=ServerSideApply=true

ok "K3s installed"

# Configure kubectl
log "Configuring kubectl..."
mkdir -p "$HOME/.kube"
sudo cp /etc/rancher/k3s/k3s.yaml "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
export KUBECONFIG="$HOME/.kube/config"
# Persist KUBECONFIG so it works in future shells
if ! grep -q 'KUBECONFIG.*kube/config' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export KUBECONFIG="$HOME/.kube/config"' >> "$HOME/.bashrc"
fi
ok "kubectl configured (run: export KUBECONFIG=~/.kube/config to activate in this shell)"

# Wait for K3s to be ready
log "Waiting for K3s to be ready..."
# First wait until the API server responds
until kubectl get nodes &>/dev/null 2>&1; do sleep 2; done
# Then wait until at least one node is registered (API can respond before any node appears)
until kubectl get nodes 2>/dev/null | grep -qE '\bReady\b|\bNotReady\b'; do sleep 2; done
kubectl wait --for=condition=Ready nodes --all --timeout=120s
ok "K3s is ready"

# Install nginx ingress controller
log "Installing nginx ingress controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
ok "nginx ingress installed"

# Install cert-manager
log "Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
ok "cert-manager installed"

# Install Helm
if ! command -v helm &>/dev/null; then
  log "Installing Helm..."
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ok "Helm installed"
else
  ok "Helm already installed: $(helm version --short)"
fi

# Add Helm repos
log "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add mongodb https://mongodb.github.io/helm-charts
helm repo update
ok "Helm repos added"

echo ""
echo -e "${GREEN}=========================================="
echo "  K3s setup complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Install operators:   ./scripts/setup/install-operators.sh"
echo "  2. Deploy InfraWatch:   ./scripts/deploy/deploy-dev.sh"
echo ""
echo "Useful commands:"
echo "  kubectl get nodes"
echo "  kubectl get pods -A"
echo "  export KUBECONFIG=~/.kube/config"
