group "default" {
    targets = ["video-processor", "video-api", "video-client"]
}

target "video-processor" {
    context = "."
    dockerfile = "dockerfiles/Dockerfile.processor"
    tags = ["video-processor:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-api" {
    context = "."
    dockerfile = "dockerfiles/Dockerfile.api"
    tags = ["video-api:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}

target "video-client" {
    context = "."
    dockerfile = "dockerfiles/Dockerfile.client"
    tags = ["video-client:latest"]
    platforms = ["linux/amd64", "linux/arm64"]
}
