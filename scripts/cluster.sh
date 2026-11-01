#!/usr/bin/env bash
# Crea o destruye el clúster k3d del proyecto plataforma-apis.
# Uso: ./scripts/cluster.sh up | down | status
set -euo pipefail

CLUSTER="plataforma"
REGISTRY="plataforma-registry"
REGISTRY_PORT="5050"

up() {
  k3d cluster create "$CLUSTER" \
    --servers 1 \
    --agents 2 \
    --k3s-arg "--disable=traefik@server:0" \
    --port "80:80@loadbalancer" \
    --port "443:443@loadbalancer" \
    --registry-create "${REGISTRY}:0.0.0.0:${REGISTRY_PORT}" \
    --wait

  # Etiqueta los agentes como nodos de trabajo (solo estético en kubectl get nodes)
  for n in $(kubectl get nodes -o name | grep agent); do
    kubectl label "$n" node-role.kubernetes.io/worker=worker --overwrite
  done

  status
  echo
  echo "Registry local: localhost:${REGISTRY_PORT} (desde el clúster: ${REGISTRY}:5000)"
}

down() {
  k3d cluster delete "$CLUSTER"
}

status() {
  kubectl cluster-info
  kubectl get nodes -o wide
}

case "${1:-}" in
  up)     up ;;
  down)   down ;;
  status) status ;;
  *) echo "Uso: $0 up | down | status"; exit 1 ;;
esac
