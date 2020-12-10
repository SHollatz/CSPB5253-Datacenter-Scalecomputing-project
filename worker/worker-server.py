#
# Worker server
#
import codecs
import hashlib
import io
import json
import numpy as np
import os
import pickle
import pika
import platform
from PIL import Image
import redis
import requests
import sys


CLASSES = [ "blank", "good", "noxtal", "strong", "weak" ]

hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
tfservingHost = os.getenv("TFSERVING_HOST") or "localhost"

modelUri = f"http://{tfservingHost}:8501/v1/models/vgg16_diff-nodiff_classification.pb:predict"

print("Connecting to rabbitmq({}). redis({}) and tfserving({})".format(rabbitMQHost,redisHost, tfservingHost))
print(f"modelUri: {modelUri}")

# Initializes RabbitMQ connection
def _getChannel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    channel = connection.channel()
    channel.queue_declare(queue='toWorker', durable=True)
    channel.exchange_declare(exchange='logs', exchange_type='topic')
    return channel

def _log(channel, routing_key, message):
    print(f"{routing_key}: {message}")
    err_log = channel.basic_publish(
        exchange='logs',
        routing_key=routing_key,
        body=message,
    )
    if (err_log):
        print("ERROR in rest-server: sendSingleImage: ", err_log)

def _processMessageCallback(ch, method, properties, body):
  # Images sent by the REST front-end have an associated hash value that is used to identify the image and a name (either file name or URL). 
  body_unpickled = pickle.loads(codecs.decode(body, "base64"))
  img_name = body_unpickled['filename']
  img_hash = body_unpickled['hash']
  img = body_unpickled['img']

  _log(ch, "worker", f" [x] Received file: {img_name}, hash: {img_hash}")
  
  # If an image hash has already been added, it doesn't need to be scanned again, but you should add the name to the set of origin names/urls for that image.
  if not redisHashToName.exists(img_hash):
    _processImage(ch, img_hash, img_name, img)
  else:
    print(f" [x] {img_name} already processed.")
    _log(ch, "worker", f" [x] Already processed file: {img_name}")

  print(f" [x] Adding to database {img_name} ({img_hash}).")
  redisHashToName.sadd(img_hash, img_name)
  redisNameToHash.set(img_name, img_hash)
  _log(ch, "worker", f" [x] Added to database HtoN and NtoH {img_name} ({img_hash})")
  # Once this process is completed, you acknowledge the message.
  ch.basic_ack(delivery_tag=method.delivery_tag)

def _processImage(ch, img_hash, img_name, img):
  print(f" [x] processing {img_name}.")
  img_nparray = np.array(img.convert('L'))
  # The worker should predict the image class
  img_gray = np.expand_dims(img_nparray, axis=-1) 
  img_to_predict = np.expand_dims(img_gray, axis=0)
  
  data = json.dumps({
        'instances': img_to_predict.tolist()
  })
  # print("data:", data)
  print("img_gray shape", img_gray.shape)
  print("img_to_predict shape", img_to_predict.shape)
  response = requests.post(modelUri, data=data.encode('utf-8'))
  print("response: ", response)
  print("response text: ", response.text)
  result = json.loads(response.text)
  predictions = np.squeeze(result['predictions'])
  predicted_class = _getClassNameFromPredictions(predictions)
  # Then, for each image, you should add the prediction and corresponding image to the Redis database. 
  _log(ch, "worker", f" [x] Add to database HtoP {img_name} ({predicted_class})")
  redisHashToPred.set(img_hash, predicted_class)

def _getClassNameFromPredictions(predictions):
  max_p = max(predictions)
  for p, c in (zip(predictions, CLASSES)):
    if p == max_p:
      print("CLASS NAME: ", c, "prediction: ", p)
      return c
  return None

def _addToSetValue(db, key, value):
  stored_set_bytes = db.get(key)
  if stored_set_bytes:
    the_set = pickle.loads(stored_set_bytes)
  else:
    the_set = set()

  the_set.add(value)

  the_set_bytes = pickle.dumps(the_set)
  db.set(key, the_set_bytes)

def configureRabbitMqReceiver():
  channel = _getChannel()
  print(' [*] Waiting for messages.')
  channel.basic_qos(prefetch_count=1)
  channel.basic_consume(queue='toWorker', on_message_callback=_processMessageCallback)
  channel.start_consuming()

# Initialize Redis
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToPred = redis.Redis(host=redisHost, db=3)

configureRabbitMqReceiver()