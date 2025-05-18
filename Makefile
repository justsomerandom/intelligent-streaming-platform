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
	@echo "  make down          Stop all running services"
	@echo "  make help          Show this help message"
	@echo ""

# Build images using Docker Compose
.PHONY: build
build:
	docker-compose -f docker/docker-compose.build.yml build

# Build specific images
.PHONY: build-processor
build-processor:
	docker-compose -f docker/docker-compose.build.yml build $(PROCESSOR)

.PHONY: build-api
build-api:
	docker-compose -f docker/docker-compose.build.yml build $(API)

.PHONY: build-client
build-client:
	docker-compose -f docker/docker-compose.build.yml build $(CLIENT)

# Build all images using Docker Bake
.PHONY: bake
bake:
	docker buildx bake --file docker/docker-bake.hcl --load

# Bake specific images
.PHONY: bake-processor
bake-processor:
	docker buildx bake --file docker/docker-bake.hcl $(PROCESSOR) --load

.PHONY: bake-api
bake-api:
	docker buildx bake --file docker/docker-bake.hcl $(API) --load

.PHONY: bake-client
bake-client:
	docker buildx bake --file docker/docker-bake.hcl $(CLIENT) --load

# Run all services using Docker Compose
.PHONY: up
up:
	docker-compose -f docker/docker-compose.yml up -d

# Stop all running services
.PHONY: down
down:
	docker-compose -f docker/docker-compose.yml down

# Remove all containers, images, and volumes
.PHONY: clean
clean:
	docker-compose -f docker/docker-compose.yml down --rmi all --volumes --remove-orphans

# Check built images and running containers
.PHONY: status
status:
	@echo "Built images:"
	@docker images | head -n 1
	@docker images | grep -w "^$(API)"
	@docker images | grep -w "^$(PROCESSOR)"
	@docker images | grep -w "^$(CLIENT)"
	@echo ""
	@echo "Running containers:"
	@docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}"
	@echo ""

# Install npm dependencies locally
.PHONY: npm-dep
npm-dep:
	npm install --prefix ./src/client

# Restart all services
.PHONY: restart
restart: down up

# Rebuild and restart all services
.PHONY: rebuild
rebuild: down build up

# Rebuild and restart all services using Docker Bake
.PHONY: rebake
rebake: down bake up