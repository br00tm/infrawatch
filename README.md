# InfraWatch

**Distributed Infrastructure Monitoring System for Kubernetes**

InfraWatch is a comprehensive monitoring solution designed to provide real-time observability for Kubernetes clusters, including metrics, logs, and alerts.

## Features

- **Real-time Metrics**: Monitor CPU, memory, disk, and network usage across your cluster
- **Centralized Logging**: Aggregate and search logs from all your applications
- **Smart Alerting**: Configure custom alert rules with multiple notification channels (Telegram, Discord, Email)
- **Modern Dashboard**: Beautiful, responsive UI built with React and TailwindCSS
- **Scalable Architecture**: Built with FastAPI, Celery, and MongoDB for high performance

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, but recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/infrawatch.git
cd infrawatch
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Start the services:
```bash
# Using Make
make dev-up

# Or using Docker Compose directly
docker-compose up -d
```

4. Access the application:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672

### Default Credentials

- **Admin User**: admin@infrawatch.local / admin123
- **RabbitMQ**: infrawatch / infrawatch123

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                   (React + TypeScript)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│                       (FastAPI)                              │
└─────────────────────────────────────────────────────────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   MongoDB   │    │    RabbitMQ     │    │    Redis    │
│  (Storage)  │    │ (Message Queue) │    │   (Cache)   │
└─────────────┘    └─────────────────┘    └─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                            │
│        (Metrics Processing, Alerts, Notifications)           │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
infrawatch/
├── backend/           # FastAPI application
├── frontend/          # React + TypeScript application
├── workers/           # Celery workers for async tasks
├── infrastructure/    # Kubernetes manifests
├── scripts/           # Utility scripts
├── docs/              # Documentation
└── docker-compose.yml # Local development setup
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
make test-backend

# Frontend tests
make test-frontend

# All tests
make test
```

## API Documentation

Once the backend is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection URL | mongodb://localhost:27017 |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | (required) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications | (optional) |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | (optional) |

## Roadmap

- [x] **Phase 1**: Core System (Backend, Frontend, Workers)
- [ ] **Phase 2**: Kubernetes Deployment & Monitoring Stack
- [ ] **Phase 3**: VPN & Security Features

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/yourusername/infrawatch/issues) page.
