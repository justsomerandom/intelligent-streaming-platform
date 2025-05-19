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

# Stream webcams for Docker
.PHONY: win-setup
win-setup:
	python ./windows/cam_setup.py

# Stop streaming webcams for Docker
.PHONY: win-teardown
win-teardown:
	./windows/cam_teardown.bat

# Run the application locally
.PHONY: run
run:
	python ./src/main.py

# Build images using Docker
.PHONY: build
build:
	docker build -t $(NAME) .

# Run all services using Docker
.PHONY: up
up:
	docker run -d --name $(NAME) -p 8080:8080 $(NAME)

# Run all services on Linux for sharing webcam
.PHONY: up-linux
up-linux:
	docker run --privileged -d --name $(NAME) --device /dev/video0:/dev/video0 -p 8080:8080 $(NAME)

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