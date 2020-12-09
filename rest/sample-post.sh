#!/bin/sh
#
# Sample queries using Curl rather than rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"localhost:5000"}
REST=${REST:-"10.107.192.176:5000"} # external ip of exposed deployment
REST=${REST:-"192.168.49.2:5000"} # minikube ip
REST=${REST:-"172.17.0.14:5000"} # frontend-ingress

curl -d '{"url":"https://storage.googleapis.com/csci4253_project_images/fake_22313"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
#
# This should match the one above
curl http://$REST/match/2474a9def68909b1cc0c7bae2c87c054de14d136d18fdf573d262b511fba72c3
#
# And this shouldn't
curl http://$REST/match/fb82e0120bbf3a26b38f6d939cb510f3ead0aa98b0afdfc972ea277e

#
# Throw in some random samples..
#
for url in $(shuf -n 10 ../sample-image-urls.txt)
do
    curl -d "{\"url\":\"$url\"}" -H "Content-Type: application/json" -X POST http://$REST/scan/url
done

# Test response with one of them:
curl http://$REST/match/1fce47b5f2b4cff761d62b20c2995c1c8788caaba8f02b4e1c14363a72443c7f