# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Make (optional)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/infrawatch.git
cd infrawatch
cp .env.example .env
```

### 2. Start Infrastructure

```bash
# Start MongoDB, Redis, RabbitMQ
docker-compose up -d mongodb redis rabbitmq
```

### 3. Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### 5. Workers Development

```bash
cd workers
pip install -r requirements.txt

# Run worker
celery -A celery_app worker --loglevel=info

# Run beat scheduler (in another terminal)
celery -A celery_app beat --loglevel=info
```

## Code Style

### Backend (Python)

- Use Black for formatting
- Use Ruff for linting
- Follow PEP 8 guidelines

```bash
# Format code
black .

# Lint code
ruff check .
ruff check --fix .
```

### Frontend (TypeScript)

- Use ESLint for linting
- Use Prettier for formatting

```bash
npm run lint
npm run format
```

## Testing

### Backend Tests

```bash
cd backend
pytest -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Git Workflow

1. Create feature branch from `main`
2. Make changes and commit with conventional commits
3. Push and create Pull Request
4. Wait for CI checks
5. Merge after approval

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Refactoring
- `test:` Tests
- `chore:` Maintenance
