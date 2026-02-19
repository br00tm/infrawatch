#!/bin/bash
# Backup MongoDB from Kubernetes pod
set -euo pipefail

NAMESPACE="${NAMESPACE:-infrawatch-data}"
BACKUP_DIR="${BACKUP_DIR:-./backups/mongodb}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"

echo "[INFO] Starting MongoDB backup to ${BACKUP_PATH}..."

# Find MongoDB pod
MONGO_POD=$(kubectl get pod -n "${NAMESPACE}" \
  -l app=infrawatch-mongodb-svc \
  -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [[ -z "${MONGO_POD}" ]]; then
  echo "[ERROR] No MongoDB pod found in namespace ${NAMESPACE}"
  exit 1
fi

echo "[INFO] Using pod: ${MONGO_POD}"

mkdir -p "${BACKUP_PATH}"

# Run mongodump inside the pod and copy out
kubectl exec -n "${NAMESPACE}" "${MONGO_POD}" -- \
  mongodump --uri="mongodb://localhost:27017/infrawatch" \
  --out="/tmp/backup_${DATE}" \
  --gzip

kubectl cp "${NAMESPACE}/${MONGO_POD}:/tmp/backup_${DATE}" "${BACKUP_PATH}"

echo "[OK] Backup saved to ${BACKUP_PATH}"
echo "[INFO] Backup size: $(du -sh "${BACKUP_PATH}" | cut -f1)"

# Keep only last 7 backups
find "${BACKUP_DIR}" -maxdepth 1 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
echo "[INFO] Old backups cleaned up"
