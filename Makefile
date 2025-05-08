# Build all images using Docker Bake
.PHONY: build
build:
	docker buildx bake

# Build specific images
.PHONY: build-ingestion
build-ingestion:
	docker buildx bake video-ingestion

.PHONY: build-analytics
build-analytics:
	docker buildx bake video-analytics

.PHONY: build-streaming
build-streaming:
	docker buildx bake video-streaming

.PHONY: build-api
build-api:
	docker buildx bake video-api

.PHONY: build-client
build-client:
	docker buildx bake video-client

# Run all services using Docker Compose
.PHONY: run
run:
	docker-compose up -d

# Stop all running services
.PHONY: stop
stop:
	docker-compose down

# Clean up dangling images and unused resources
.PHONY: clean
clean:
	docker system prune -f --volumes