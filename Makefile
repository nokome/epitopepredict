# Build the image
build:
	#tar xvzf netMHCpan-4.0a.Linux.tar.gz
	#curl http://www.cbs.dtu.dk/services/NetMHCpan-4.0/data.Linux.tar.gz -o netMHCpan-4.0/data.Linux.tar.gz
	#cd netMHCpan-4.0/ && tar xvzf data.Linux.tar.gz
	#rm netMHCpan-4.0/data.Linux.tar.gz
	#docker build --tag stencila/epitopepredict .

# Run the image
run:
	docker run -it --rm stencila/epitopepredict