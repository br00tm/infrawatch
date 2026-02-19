# InfraWatch Architecture

## Overview

InfraWatch is built using a microservices architecture with the following main components:

## Components

### Backend (FastAPI)

The backend is a Python FastAPI application that provides:
- RESTful API endpoints
- WebSocket support for real-time updates
- JWT-based authentication
- MongoDB integration via Motor (async driver)

**Key Modules:**
- `api/v1/`: API endpoints (auth, metrics, logs, alerts)
- `models/`: MongoDB document models
- `schemas/`: Pydantic schemas for validation
- `repositories/`: Data access layer
- `services/`: Business logic layer
- `core/`: Security, logging, exceptions

### Frontend (React + TypeScript)

Modern single-page application built with:
- React 18 with TypeScript
- TailwindCSS for styling
- Zustand for state management
- React Router for navigation
- Recharts for visualizations
- Axios for API communication

### Workers (Celery)

Background task processing for:
- Metric aggregation
- Alert rule evaluation
- Notification delivery
- Data cleanup

### Data Storage

- **MongoDB**: Primary database for metrics, logs, alerts, users
- **Redis**: Caching and Celery broker/backend
- **RabbitMQ**: Message queue (optional, alternative to Redis)

## Data Flow

```
1. Metrics/Logs → Backend API → MongoDB
                            ↓
                      RabbitMQ/Redis
                            ↓
                    Celery Workers → Process & Alert
                            ↓
                    Notifications (Telegram/Discord/Email)
```

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting (planned)
- Network policies in K8s (Phase 2)

## Scalability

- Horizontal scaling of backend with load balancer
- Multiple Celery workers
- MongoDB replica set (Phase 2)
- Redis Sentinel (Phase 2)
