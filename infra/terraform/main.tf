# =====================================================================
# Terraform: instala el operador CloudNativePG en el clúster k3d
# Ciclo: terraform init → fmt → validate → plan -out=tfplan → apply tfplan
# =====================================================================

# ---------------------------------------------------------------------
# 1. Configuración de Terraform: qué providers necesita este proyecto
#    (como "required_providers" del ejercicio de Docker)
# ---------------------------------------------------------------------
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm" # dónde se publica el provider
      version = "~> 3.0"         # cualquier 3.x, nunca la 4 (cambios mayores)
    }
  }
}

# ---------------------------------------------------------------------
# 2. Provider Helm: a qué clúster de Kubernetes conectarse
#    Usa el mismo kubeconfig que kubectl.
# ---------------------------------------------------------------------
provider "helm" {
  kubernetes = {
    config_path    = "~/.kube/config" # archivo con las credenciales del clúster
    config_context = "k3d-plataforma" # protección: SOLO este clúster, aunque
    # el kubeconfig tenga otros (ej. un EKS)
  }
}

# ---------------------------------------------------------------------
# 3. Recurso: un release de Helm = un chart instalado en el clúster
#    Equivale a:
#    helm install cnpg cnpg/cloudnative-pg --version 0.29.1 \
#      --namespace cnpg-system --create-namespace --wait
# ---------------------------------------------------------------------
resource "helm_release" "cnpg" {
  # Nombre del release en el clúster (lo verás con: helm list -A)
  name = "cnpg"

  # De dónde se descarga el chart (el repositorio)
  repository = "https://cloudnative-pg.github.io/charts"

  # Qué chart instalar (el paquete)
  chart = "cloudnative-pg"

  # Versión EXACTA del chart (CHART VERSION, no APP VERSION).
  # Fijarla hace la instalación reproducible, igual que uv.lock.
  # Chart 0.29.1 instala el operador 1.30.1.
  version = "0.29.1"

  # Namespace donde vivirá el operador; se crea si no existe
  namespace        = "cnpg-system"
  create_namespace = true

  # El apply espera a que los pods del operador estén listos,
  # no solo a que Kubernetes reciba la orden
  wait = true
}

# ---------------------------------------------------------------------
# Notas:
# - El state (terraform.tfstate) queda en esta carpeta y NO va a Git.
# - Terraform ve UN solo recurso, aunque el chart cree decenas de
#   objetos en Kubernetes (Deployments, RBAC, CRDs, webhooks...).
#   Los detalles los administra Helm.
# - Para ver lo instalado:
#     helm list -n cnpg-system
#     kubectl -n cnpg-system get pods
#     kubectl get crd | grep cnpg
# ---------------------------------------------------------------------