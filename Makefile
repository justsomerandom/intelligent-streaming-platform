# Define container/image names
NAME=intelligent-streaming-platform

# Print help message
.PHONY: help
help:
	@echo "Makefile for Docker Compose and Docker Bake"
	@echo ""
	@echo "Usage:"
	@echo "  make build         Build Docker container"
	@echo "  make up            Run all services using Docker"
	@echo "  make down          Stop all running services"
	@echo "  make clean         Remove Docker image"
	@echo "  make restart       Restart all services"
	@echo "  make rebuild       Rebuild and restart all services"
	@echo "  make help          Show this help message"
	@echo ""

# Build images using Docker Compose
.PHONY: build
build:
	docker build -t $(NAME) .

# Run all services using Docker Compose
.PHONY: up
up:
	docker run -d --name $(NAME) -p 8000:8000 -p 8554:8554 -p 8556:8556 $(NAME)

# Stop all running services
.PHONY: down
down:
	docker stop $(NAME) && docker rm $(NAME)

# Remove all containers, images, and volumes
.PHONY: clean
clean:
	docker rmi $(NAME)

# Restart all services
.PHONY: restart
restart: down up

# Rebuild and restart all services
.PHONY: rebuild
rebuild: down build up