#!/bin/bash
# Install Kubernetes operators required by InfraWatch
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }

NAMESPACE_DATA="infrawatch-data"
NAMESPACE_MONITORING="infrawatch-monitoring"

# Create namespaces
log "Creating namespaces..."
kubectl apply -f infrastructure/kubernetes/base/namespace.yaml
ok "Namespaces ready"

# ── MongoDB Community Operator ──────────────────────────────────────────────
log "Installing MongoDB Community Operator..."
helm repo add mongodb https://mongodb.github.io/helm-charts
helm repo update
helm upgrade --install mongodb-community-operator mongodb/community-operator \
  --namespace "${NAMESPACE_DATA}" \
  --create-namespace \
  --set operator.watchNamespace="${NAMESPACE_DATA}"
ok "MongoDB Operator installed"

# ── RabbitMQ Cluster Operator ────────────────────────────────────────────────
log "Installing RabbitMQ Cluster Operator..."
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
kubectl wait --namespace rabbitmq-system \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=rabbitmq-cluster-operator \
  --timeout=120s
ok "RabbitMQ Operator installed"

# ── kube-prometheus-stack ─────────────────────────────────────────────────────
# Create Grafana dashboard ConfigMap BEFORE installing the chart (Grafana init container needs it)
log "Creating Grafana dashboard ConfigMap..."
kubectl create namespace "${NAMESPACE_MONITORING}" --dry-run=client -o yaml | kubectl apply -f -
kubectl create configmap infrawatch-grafana-dashboards \
  --namespace "${NAMESPACE_MONITORING}" \
  --from-file=cluster-overview.json=infrastructure/kubernetes/infrastructure/monitoring/grafana/dashboards/cluster-overview.json \
  --dry-run=client -o yaml | kubectl apply -f -
ok "Grafana dashboards ConfigMap ready"

log "Installing kube-prometheus-stack..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace "${NAMESPACE_MONITORING}" \
  --create-namespace \
  --values infrastructure/kubernetes/infrastructure/monitoring/prometheus/prometheus-values.yaml \
  --timeout 10m \
  --wait
ok "kube-prometheus-stack installed"

# ── Loki ──────────────────────────────────────────────────────────────────────
log "Installing Loki..."
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install loki grafana/loki \
  --namespace "${NAMESPACE_MONITORING}" \
  --values infrastructure/kubernetes/infrastructure/monitoring/loki/loki-values.yaml \
  --wait
ok "Loki installed"

# ── Promtail ──────────────────────────────────────────────────────────────────
log "Installing Promtail..."
helm upgrade --install promtail grafana/promtail \
  --namespace "${NAMESPACE_MONITORING}" \
  --values infrastructure/kubernetes/infrastructure/monitoring/loki/promtail-config.yaml \
  --wait
ok "Promtail installed"

echo ""
echo -e "${GREEN}=========================================="
echo "  All operators installed!"
echo "==========================================${NC}"
echo ""
echo "Grafana:    http://$(kubectl get svc -n ${NAMESPACE_MONITORING} kube-prometheus-stack-grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):80"
echo "Prometheus: http://$(kubectl get svc -n ${NAMESPACE_MONITORING} kube-prometheus-stack-prometheus -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):9090"
