# Base this image on https://hub.docker.com/r/stencila/executa-all
# which has Stencila executors and Python already installed
FROM stencila/executa-all:20210129.1

USER root

# Install tsch needed for netMHC
RUN apt-get update && apt-get install tcsh

# Install epitopepredict
RUN pip3 install epitopepredict

# Install requirements e.g matplotlib, mhcflurry
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy over netMHCpan and netMHCIIpan and symlink so in $PATH
COPY --chown=guest:guest netMHCpan-4.0/ /usr/bin/netMHCpan-4.0/
COPY --chown=guest:guest netMHCIIpan-3.0/ /usr/bin/netMHCIIpan-3.0/
RUN ln -s /usr/bin/netMHCpan-4.0/netMHCpan /usr/bin/netMHCpan; \
    ln -s /usr/bin/netMHCIIpan-3.0/netMHCIIpan /usr/bin/netMHCIIpan; \
    chmod +x /usr/bin/netMHCpan; \
    chmod +x /usr/bin/netMHCIIpan

# Edit the environment variables as per netMHC instructions
RUN sed -e 's!setenv\tNMHOME.*$!setenv NMHOME /usr/bin/netMHCpan-4.0!g' \
        -e 's!setenv  TMPDIR.*$!setenv  TMPDIR /tmp!g' -i /usr/bin/netMHCpan-4.0/netMHCpan
RUN sed -e 's!setenv\tNMHOME.*$!setenv NMHOME /usr/bin/netMHCIIpan-3.0!g' \
        -e 's!setenv  TMPDIR.*$!setenv  TMPDIR /tmp!g' -i /usr/bin/netMHCIIpan-3.0/netMHCIIpan

USER guest
