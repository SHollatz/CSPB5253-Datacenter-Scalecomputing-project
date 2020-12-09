#!/usr/bin/env python3
# 
#
# A sample REST client for the face match application
#
import requests
import json
import time
import sys, os
import jsonpickle

def doImage(addr, filename, debug=False):
    # prepare headers for http request
    print("inside client doImage addr: ", addr)
    headers = {'content-type': 'image/jpg'}
    img = open(filename, 'rb').read()
    # send http request with image and receive response
    image_url = addr + '/scan/image' + "/" + os.path.basename(filename)
    print("image_url: ", image_url)
    response = requests.post(image_url, data=img, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def doUrl(addr, filename, debug=False):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    # send http request with image and receive response
    image_url = addr + '/scan/url'
    data = jsonpickle.encode({ "url" : filename})
    response = requests.post(image_url, data=data, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def doMatch(addr, hashval, debug=False):
    url = addr + "/match/" + hashval
    response = requests.get(url)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

if cmd == 'image':
    filename = sys.argv[3]
    reps = int(sys.argv[4])
    start = time.perf_counter()
    for x in range(reps):
        doImage(addr, filename, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'url':
    url = sys.argv[3]
    reps = int(sys.argv[4])
    start = time.perf_counter()
    for x in range(reps):
        doUrl(addr, url, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'match':
    hashval = sys.argv[3]
    reps = int(sys.argv[4])
    start = time.perf_counter()
    for x in range(reps):
        doMatch(addr, hashval, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
else:
    print("Unknown option", cmd)