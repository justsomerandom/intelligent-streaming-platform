# Define container/image names
API=video-api
PROCESSOR=video-processor
CLIENT=video-client

# Print help message
.PHONY: help
help:
	@echo "Makefile for Docker Compose and Docker Bake"
	@echo ""
	@echo "Usage:"
	@echo "  make build          Build containers using Docker Compose"
	@echo "  make bake           Build all images using Docker Bake"
	@echo "  make bake-processor Build processor image using Docker Bake"
	@echo "  make bake-api       Build API image using Docker Bake"
	@echo "  make bake-client    Build client image using Docker Bake"
	@echo "  make up            Run all services using Docker Compose"
	@echo "  make upx           Force services to use baked images"
	@echo "  make down          Stop all running services"
	@echo "  make help          Show this help message"
	@echo ""

# Build containers directly using Docker Compose
.PHONY: build
build:
	docker-compose -f docker/docker-compose.build.yml build

# Build all images using Docker Bake
.PHONY: bake
bake:
	docker buildx bake --file docker/docker-bake.hcl --load

# Bake specific images
.PHONY: bake-processor
build-processor:
	docker buildx bake --file docker/docker-bake.hcl $(PROCESSOR) --load

.PHONY: bake-api
build-api:
	docker buildx bake --file docker/docker-bake.hcl $(API) --load

.PHONY: bake-client
build-client:
	docker buildx bake --file docker/docker-bake.hcl $(CLIENT) --load

# Run all services using Docker Compose
.PHONY: up
up:
	@if [ $(shell docker-compose -f docker/docker-compose.build.yml images -q) ]; then \
		docker-compose -f docker/docker-compose.build.yml up -d; \
	else \
		docker-compose -f docker/docker-compose.yml up -d; \
	fi

# Force services to use baked images
.PHONY: upx
upx:
	docker-compose -f docker/docker-compose.yml up -d

# Stop all running services
.PHONY: down
down:
	docker-compose -f docker/docker-compose.yml down