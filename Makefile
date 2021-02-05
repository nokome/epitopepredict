netMHCpan-4.0:
	tar xvzf netMHCpan-4.0a.Linux.tar.gz
	curl http://www.cbs.dtu.dk/services/NetMHCpan-4.0/data.Linux.tar.gz -o netMHCpan-4.0/data.Linux.tar.gz
	cd netMHCpan-4.0 && tar xvzf data.Linux.tar.gz
	rm netMHCpan-4.0/data.Linux.tar.gz

netMHCIIpan-3.0:
	tar xvzf netMHCIIpan-3.0c.Linux.tar.gz
	curl http://www.cbs.dtu.dk/services/NetMHCIIpan-3.0/data.tar.gz -o netMHCIIpan-3.0/data.tar.gz
	cd netMHCIIpan-3.0 && tar xvzf data.tar.gz
	rm netMHCIIpan-3.0/data.tar.gz

# Build the image
build: netMHCpan-4.0 netMHCIIpan-3.0
	docker build --tag stencila/epitopepredict .

# Run the image
run:
	docker run -it --rm stencila/epitopepredict