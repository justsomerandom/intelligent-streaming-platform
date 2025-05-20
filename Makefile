# Print help message
.PHONY: help
help:
	@echo "Makefile for Docker Compose and Docker Bake"
	@echo ""
	@echo "Usage:"
	@echo "  make run			Run the application locally"
	@echo "  make play 		   	Run the video player
	@echo "  make help          Show this help message"
	@echo ""


# Run the application locally
.PHONY: run
run:
	python ./src/main.py

# Run the video player
.PHONY: play
play:
	python ./src/player/player.py