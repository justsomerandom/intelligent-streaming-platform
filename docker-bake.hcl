group "default" {
    targets = ["video-ingestion", "video-analytics", "video-streaming", "video-api", "video-client"]
}

target "video-ingestion" {
    context = "."
    dockerfile = "docker/dockerfiles/Dockerfile.ingestion"
    tags = ["video-ingestion:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-analytics" {
    context = "."
    dockerfile = "docker/dockerfiles/Dockerfile.analytics"
    tags = ["video-analytics:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-streaming" {
    context = "."
    dockerfile = "docker/dockerfiles/Dockerfile.streaming"
    tags = ["video-streaming:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-api" {
    context = "."
    dockerfile = "docker/dockerfiles/Dockerfile.api"
    tags = ["video-api:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-client" {
    context = "."
    dockerfile = "docker/dockerfiles/Dockerfile.client"
    tags = ["video-client:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}
