# Template Solventa Backend Services

FastAPI monorepo with services.

## Requirements

- Python 3.13+
- Docker Compose

## Run locally

Install greeting service dependencies and run it:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r greeting_service/requirements.txt
uvicorn src.main:app --reload --app-dir greeting_service
```

Install math service dependencies separately with `pip install -r math_service/requirements.txt`.

Run both services and their shared dependencies with Compose:

```bash
docker compose up --build
```

The greeting API is available at `http://localhost:8000`; the math API is at `http://localhost:8001`.

## APIs

- Greeting service: `GET /health`, `GET /greetings/`, `POST /greetings/`
- Math service: `GET /health`, `POST /add`

## Source layout

- `greeting_service/src`: greeting API and Clean Architecture layers
- `greeting_service/requirements.txt`: greeting service dependencies
- `greeting_service/tests`: greeting service unit and integration tests
- `math_service/src`: stateless math API and its application layers
- `math_service/requirements.txt`: math service dependencies
- `math_service/tests`: math service unit and integration tests
- `docker-compose.yml`: local Docker Compose configuration
- `docker/services/Dockerfile.<service_name>`: service-specific images
- `deployment/helm/config/<service_name>/values.yaml`: per-service Helm settings

Run each service's tests separately from the repository root:

```bash
PYTHONPATH=greeting_service python -m pytest greeting_service/tests
PYTHONPATH=math_service python -m pytest math_service/tests
```

## Deployment configuration

All workflows are started manually from **Actions** with `workflow_dispatch`:

- `eks-setup-init.yml`: creates the environment's Kubernetes namespace and applies its Kustomize resources, including an ExternalSecret that syncs the environment's Secrets Manager secret into Kubernetes. Input: `target_env`.
- `eks-setup-ingress.yml`: applies the selected environment's Kustomize ingress overlay. Input: `target_env`.
- `backend-publish-ecr.yml`: builds and pushes images for both `greeting_service` and `math_service` to their ECR repositories. Input: `target_env`.
- `service-publish-ecr.yml`: builds and pushes one service image to its ECR repository. Inputs: `target_env`, `service_name`.
- `backend-deploy-eks.yml`: deploys both services to EKS in parallel using Helm and waits for each rollout. Input: `target_env`.
- `service-deploy-eks.yml`: deploys one selected service to EKS using Helm and waits for its rollout. Inputs: `target_env`, `service_name`.

For image publishing, set each service's `image.repository` in its environment-specific Helm values file to the ECR repository URI.

### Environments

Create these GitHub Environments with matching names; each workflow's `target_env` input selects one:

- `dev` uses cluster `solventa-dev-eks` and namespace `solventa-dev`.
- `qa` uses cluster `solventa-qa-eks` and namespace `solventa-qa`.
- `prod` uses cluster `solventa-prod-eks` and namespace `solventa-prod`.

### Required secrets

Add these secrets separately to each GitHub Environment (`dev`, `qa`, and `prod`):

- `AWS_REGION`: AWS region containing the environment's EKS cluster and ECR repositories.
- `AWS_ROLE_ARN`: IAM role ARN assumed by GitHub Actions using OIDC.
- `DATABASE_URL`: greeting service database connection string; `eks-setup-init.yml` writes it to Kubernetes.

The External Secrets Operator must be installed in each cluster. Its controller must have AWS Pod Identity credentials and permission to read the environment's `solventa-backend/app-secrets` secret in Secrets Manager.
