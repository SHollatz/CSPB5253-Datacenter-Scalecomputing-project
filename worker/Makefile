##
## You provide this to build your docker image
##
worker-server: worker-server.py
	docker build -f Dockerfile-worker -t worker:v1 .
	docker run --rm -it -v $(pwd)/.:/app dirkcgrunwald/facerec:v1 /bin/bash

run:
	python3 worker-server.py

clean:
	python3 drop-redis.py