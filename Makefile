.PHONY: help build up down logs restart clean test

help:
	@echo "NIFTY Alerter Service - Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start services"
	@echo "  make down     - Stop services"
	@echo "  make logs     - View logs"
	@echo "  make restart  - Restart services"
	@echo "  make clean    - Remove all containers and volumes"
	@echo "  make test     - Run tests"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec nifty-alerter python -m pytest
