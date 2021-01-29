# Build the image
build:
	docker build --tag stencila/epitopepredict .

# Run the image
run:
	docker run -it --rm stencila/epitopepredict