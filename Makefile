# Build all images using Docker Bake
.PHONY: build
build:
	docker buildx bake --file docker/docker-bake.hcl --load

# Build specific images
.PHONY: build-ingestion
build-ingestion:
	docker buildx bake --file docker/docker-bake.hcl video-ingestion --load

.PHONY: build-analytics
build-analytics:
	docker buildx bake --file docker/docker-bake.hcl video-analytics --load

.PHONY: build-streaming
build-streaming:
	docker buildx bake --file docker/docker-bake.hcl video-streaming --load

.PHONY: build-api
build-api:
	docker buildx bake --file docker/docker-bake.hcl video-api --load

.PHONY: build-client
build-client:
	docker buildx bake --file docker/docker-bake.hcl video-client --load

# Run all services using Docker Compose
.PHONY: run
run:
	docker-compose -f docker/docker-compose.yml up -d 

# Stop all running services
.PHONY: stop
stop:
	docker-compose -f docker/docker-compose.yml down

# Clean up dangling images and unused resources
.PHONY: clean
clean:
	docker system prune -f --volumes