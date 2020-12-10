#!/bin/sh
#
# Sample use of ./rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"localhost:5000"}
REST=${REST:-"192.168.49.2"} # frontend-ingress

./rest-client.py $REST url https://storage.googleapis.com/csci4253_project_images/fake_20803.png 10


#
# Throw in some random samples..
#
for url in $(shuf -n 10 ../sample-image-urls.txt)
do
    ./rest-client.py $REST url "$url" 10
done