#!/bin/sh
#
# Sample queries using Curl rather than rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"localhost:5000"}
REST=${REST:-"192.168.49.2"} # frontend-ingress

curl -d '{"url":"https://storage.googleapis.com/csci4253_project_images/fake_20803.png"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
