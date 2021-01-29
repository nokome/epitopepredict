# Base this image on https://hub.docker.com/r/stencila/executa-all
# which has Stencila executors and Python already installed
FROM stencila/executa-all:20210129.1

# Install epitopepredict
USER root
RUN pip3 install epitopepredict
USER guest
