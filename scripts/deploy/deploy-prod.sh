#!/bin/bash
# Deploy InfraWatch to production using Helm
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"
REGISTRY="${REGISTRY:?REGISTRY env var required}"
DOMAIN="${DOMAIN:?DOMAIN env var required (e.g. infrawatch.yourcompany.com)}"

# Validate required secrets are set
: "${MONGODB_PASSWORD:?MONGODB_PASSWORD required}"
: "${RABBITMQ_PASSWORD:?RABBITMQ_PASSWORD required}"
: "${JWT_SECRET_KEY:?JWT_SECRET_KEY required}"
: "${GRAFANA_PASSWORD:?GRAFANA_PASSWORD required}"

log "Deploying InfraWatch ${IMAGE_TAG} to production..."
log "Domain: ${DOMAIN}"

# Update Helm deps
helm dependency update charts/infrawatch/

# Deploy via Helm
helm upgrade --install infrawatch charts/infrawatch/ \
  --namespace infrawatch \
  --create-namespace \
  --values charts/infrawatch/values.yaml \
  --values charts/infrawatch/values-prod.yaml \
  --set "backend.image.tag=${IMAGE_TAG}" \
  --set "frontend.image.tag=${IMAGE_TAG}" \
  --set "worker.image.tag=${IMAGE_TAG}" \
  --set "beat.image.tag=${IMAGE_TAG}" \
  --set "frontend.ingress.hosts[0].host=${DOMAIN}" \
  --set "frontend.ingress.tls[0].hosts[0]=${DOMAIN}" \
  --set "mongodb.auth.rootPassword=${MONGODB_PASSWORD}" \
  --set "mongodb.auth.password=${MONGODB_PASSWORD}" \
  --set "rabbitmq.auth.password=${RABBITMQ_PASSWORD}" \
  --set "backend.secrets.jwtSecretKey=${JWT_SECRET_KEY}" \
  --set "backend.secrets.mongodbUrl=mongodb://infrawatch:${MONGODB_PASSWORD}@infrawatch-mongodb:27017/infrawatch?authSource=admin" \
  --set "backend.secrets.redisUrl=redis://infrawatch-redis-master:6379/0" \
  --set "backend.secrets.rabbitmqUrl=amqp://infrawatch:${RABBITMQ_PASSWORD}@infrawatch-rabbitmq:5672/" \
  --timeout 10m \
  --wait \
  --atomic

ok "Production deployment complete!"

# Show status
kubectl get pods -n infrawatch
kubectl get ingress -n infrawatch
