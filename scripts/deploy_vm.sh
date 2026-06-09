#!/usr/bin/env bash
set -euo pipefail

# Rebuild and restart the VM Docker container without losing the SQLite DB.
# The database lives on the host in ./instance/greenlife.db and is mounted into
# the container at /app/instance/greenlife.db.

APP_NAME="${APP_NAME:-software_project_2}"
IMAGE_NAME="${IMAGE_NAME:-software_project_2-web:latest}"
HOST_PORT="${HOST_PORT:-80}"
CONTAINER_PORT="${CONTAINER_PORT:-5001}"

cd "$(dirname "$0")/.."

mkdir -p instance logs

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
fi

"${DOCKER[@]}" build --no-cache -t "$IMAGE_NAME" .

"${DOCKER[@]}" stop "$APP_NAME" 2>/dev/null || true
"${DOCKER[@]}" rm "$APP_NAME" 2>/dev/null || true

ENV_ARGS=()
if [ -f .env ]; then
  ENV_ARGS=(--env-file .env)
fi

"${DOCKER[@]}" run -d \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  --name "$APP_NAME" \
  "${ENV_ARGS[@]}" \
  -v "$PWD/instance:/app/instance" \
  -v "$PWD/logs:/app/logs" \
  "$IMAGE_NAME"

echo "Started $APP_NAME from $IMAGE_NAME"
echo "Database persists at: $PWD/instance/greenlife.db"
