#!/bin/bash
# Check health of all InfraWatch services
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; FAILED=$((FAILED+1)); }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }

NAMESPACE="${NAMESPACE:-infrawatch}"
NAMESPACE_DATA="${NAMESPACE_DATA:-infrawatch-data}"
FAILED=0

echo "=========================================="
echo "  InfraWatch Health Check"
echo "=========================================="
echo ""

# ── Kubernetes Pods ───────────────────────────────────────────────────────────
echo "Pods (${NAMESPACE}):"
while IFS= read -r line; do
  pod=$(echo "$line" | awk '{print $1}')
  ready=$(echo "$line" | awk '{print $2}')
  status=$(echo "$line" | awk '{print $3}')
  if [[ "$status" == "Running" ]]; then
    ok "  ${pod} — ${ready} (${status})"
  elif [[ "$status" == "Completed" ]]; then
    warn "  ${pod} — ${status}"
  else
    fail "  ${pod} — ${ready} (${status})"
  fi
done < <(kubectl get pods -n "${NAMESPACE}" --no-headers 2>/dev/null || echo "")

echo ""
echo "Pods (${NAMESPACE_DATA}):"
while IFS= read -r line; do
  pod=$(echo "$line" | awk '{print $1}')
  status=$(echo "$line" | awk '{print $3}')
  if [[ "$status" == "Running" ]]; then
    ok "  ${pod} (${status})"
  else
    fail "  ${pod} (${status})"
  fi
done < <(kubectl get pods -n "${NAMESPACE_DATA}" --no-headers 2>/dev/null || echo "")

echo ""
echo "API Health:"
# Port-forward temporarily if needed
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
if curl -sf "${BACKEND_URL}/health" &>/dev/null; then
  ok "  Backend API is healthy (${BACKEND_URL})"
else
  fail "  Backend API is unreachable (${BACKEND_URL})"
fi

echo ""
echo "HPA Status:"
kubectl get hpa -n "${NAMESPACE}" 2>/dev/null | while IFS= read -r line; do
  echo "  $line"
done

echo ""
echo "PVC Status:"
kubectl get pvc -n "${NAMESPACE_DATA}" 2>/dev/null | while IFS= read -r line; do
  echo "  $line"
done

echo ""
echo "=========================================="
if [[ $FAILED -eq 0 ]]; then
  echo -e "${GREEN}  All checks passed!${NC}"
else
  echo -e "${RED}  ${FAILED} check(s) failed!${NC}"
  exit 1
fi
echo "=========================================="
