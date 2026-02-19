.PHONY: help dev-up dev-down dev-logs dev-rebuild test lint format clean

# ===================
# HELP
# ===================
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ===================
# DEVELOPMENT
# ===================
dev-up: ## Start development environment
	docker-compose up -d

dev-down: ## Stop development environment
	docker-compose down

dev-logs: ## View logs
	docker-compose logs -f

dev-rebuild: ## Rebuild and restart all services
	docker-compose up -d --build

dev-restart: ## Restart all services
	docker-compose restart

# ===================
# INDIVIDUAL SERVICES
# ===================
backend-shell: ## Open shell in backend container
	docker-compose exec backend bash

frontend-shell: ## Open shell in frontend container
	docker-compose exec frontend sh

db-shell: ## Open MongoDB shell
	docker-compose exec mongodb mongosh -u infrawatch -p infrawatch123 infrawatch

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

# ===================
# TESTING
# ===================
test-backend: ## Run backend tests
	cd backend && python -m pytest -v --cov=app

test-frontend: ## Run frontend tests
	cd frontend && npm run test

test: test-backend test-frontend ## Run all tests

# ===================
# LINTING & FORMATTING
# ===================
lint-backend: ## Lint backend code
	cd backend && ruff check . && black --check .

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

lint: lint-backend lint-frontend ## Lint all code

format-backend: ## Format backend code
	cd backend && black . && ruff check --fix .

format-frontend: ## Format frontend code
	cd frontend && npm run format

format: format-backend format-frontend ## Format all code

# ===================
# DATABASE
# ===================
db-backup: ## Backup MongoDB
	./scripts/backup/backup-mongodb.sh

db-restore: ## Restore MongoDB (usage: make db-restore BACKUP_FILE=path/to/backup)
	./scripts/backup/restore-mongodb.sh $(BACKUP_FILE)

# ===================
# CLEANUP
# ===================
clean: ## Clean up development environment
	docker-compose down -v
	docker system prune -f

clean-all: ## Clean everything including images
	docker-compose down -v --rmi all
	docker system prune -af

# ===================
# INSTALL
# ===================
install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

install: install-backend install-frontend ## Install all dependencies

# ===================
# BUILD
# ===================
build-backend: ## Build backend image
	docker build -t infrawatch-backend ./backend

build-frontend: ## Build frontend image
	docker build -t infrawatch-frontend ./frontend

build-workers: ## Build workers image
	docker build -t infrawatch-workers ./workers

build: build-backend build-frontend build-workers ## Build all images

# ===================
# LOGS
# ===================
logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-worker: ## View worker logs
	docker-compose logs -f worker

logs-mongodb: ## View MongoDB logs
	docker-compose logs -f mongodb
