#!/bin/bash
# Setup local development environment

set -e

echo "=========================================="
echo "InfraWatch - Local Development Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}Docker and Docker Compose are installed.${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created.${NC}"
else
    echo -e "${YELLOW}.env file already exists.${NC}"
fi

# Start services
echo -e "${YELLOW}Starting services with Docker Compose...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    echo -e "${GREEN}MongoDB is healthy.${NC}"
else
    echo -e "${RED}MongoDB is not responding.${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}Redis is healthy.${NC}"
else
    echo -e "${RED}Redis is not responding.${NC}"
fi

# Check RabbitMQ
if docker-compose exec -T rabbitmq rabbitmq-diagnostics check_running &> /dev/null; then
    echo -e "${GREEN}RabbitMQ is healthy.${NC}"
else
    echo -e "${RED}RabbitMQ is not responding.${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup complete!${NC}"
echo "=========================================="
echo ""
echo "Services are running at:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Frontend:    http://localhost:3000"
echo "  - RabbitMQ:    http://localhost:15672 (guest/guest)"
echo ""
echo "Default credentials:"
echo "  - Admin: admin@infrawatch.local / admin123"
echo ""
echo "Useful commands:"
echo "  - View logs:    make dev-logs"
echo "  - Stop:         make dev-down"
echo "  - Restart:      make dev-restart"
echo ""
