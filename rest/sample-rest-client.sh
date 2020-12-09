#!/bin/sh
#
# Sample use of ./rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"localhost:5000"}

./rest-client.py $REST url https://storage.googleapis.com/cu-csci-5253/lfw/Zico/Zico_0003.jpg 10
#
# match above
#
./rest-client.py $REST match 215a00cf1bc966348bbd55aa0c8a8b82d1636a68e7d60fdf790329e2 10
#
# no match above
#
./rest-client.py $REST match fb82e0120bbf3a26b38f6d939cb510f3ead0aa98b0afdfc972ea277e 10

#
# Throw in some random samples..
#
for url in $(shuf -n 10 ../all-image-urls.txt)
do
    ./rest-client.py $REST url "$url" 10
done