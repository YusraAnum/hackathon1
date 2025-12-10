# Deployment Configuration

This directory contains production-ready deployment configurations for the AI-Native Textbook application.

## Docker Deployment

### Production Deployment

To deploy the application using Docker Compose in production:

```bash
# Create a .env file with your environment variables
cp .env.example .env
# Edit .env with your actual values

# Deploy in production mode
docker-compose -f deploy/docker/docker-compose.prod.yml up -d
```

### Development Deployment

To deploy the application using Docker Compose for development:

```bash
# Deploy in development mode with hot-reloading
docker-compose -f deploy/docker/docker-compose.dev.yml up -d
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.20+)
- kubectl configured to connect to your cluster
- cert-manager installed (for TLS certificates)

### Production Deployment

1. Create the textbook namespace:
```bash
kubectl create namespace textbook
```

2. Create secrets for sensitive data:
```bash
kubectl create secret generic textbook-secrets \
  --namespace=textbook \
  --from-literal=neon-db-url=<your-neon-db-url> \
  --from-literal=qdrant-url=<your-qdrant-url> \
  --from-literal=qdrant-api-key=<your-qdrant-api-key> \
  --from-literal=openai-api-key=<your-openai-api-key> \
  --from-literal=postgres-password=<your-postgres-password>
```

3. Deploy the application:
```bash
kubectl apply -f deploy/kubernetes/production.yaml
```

## Environment Variables

The following environment variables are required for production deployment:

- `NEON_DB_URL`: PostgreSQL database URL
- `QDRANT_URL`: Qdrant vector database URL
- `QDRANT_API_KEY`: Qdrant API key
- `OPENAI_API_KEY`: OpenAI API key
- `POSTGRES_USER`: PostgreSQL username (default: textbook_user)
- `POSTGRES_PASSWORD`: PostgreSQL password

## Security Features

- Security headers configured at application and infrastructure level
- Non-root containers for improved security
- Resource limits to prevent resource exhaustion
- Health checks for automatic failover
- Rate limiting to prevent abuse
- SSL/TLS termination with Let's Encrypt

## Monitoring and Logging

- Application logs are written to `/app/logs` in the backend container
- Structured JSON logging for easy parsing and analysis
- Kubernetes liveness and readiness probes for automatic recovery
- Health check endpoints at `/health`

## Scaling

The Kubernetes configuration includes 3 replicas for high availability. You can scale the deployments as needed:

```bash
kubectl scale deployment ai-native-textbook-backend --replicas=5 --namespace=textbook
kubectl scale deployment ai-native-textbook-frontend --replicas=5 --namespace=textbook
```