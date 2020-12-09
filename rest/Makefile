##
## You provide this to build and push your docker images
##
worker-server: rest-server.py
	docker build -f Dockerfile-rest -t restserver:v1 .
	docker run --rm -it -v $(pwd)/.:/app restserver:v1 /bin/bash

run:
	python3 /app/rest-server.py

