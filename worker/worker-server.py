#
# Worker server
#
import codecs
import face_recognition
import hashlib
import io
import numpy as np
import os
import pickle
import pika
import platform
from PIL import Image
import redis
import sys


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

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
  img_nparray = np.array(img.convert('RGB'))
  # The worker should extract the list of faces in the image using face_recognition.face_encodings. 
  unknown_face_encodings = face_recognition.face_encodings(img_nparray)
  # Then, for each face in that list, you should add the face and corresponding image to the Redis database and then compare those faces to all other faces in each image the database. 
  _log(ch, "worker", f" [x] Add to database HtoF {img_name} ({img_hash})")
  face_encodings_pickled = [pickle.dumps(f) for f in unknown_face_encodings]
  redisHashToFaceRec.sadd(img_hash, *face_encodings_pickled)
  # For each image containing any matching face, you would add the images (hashes) of each image to the other such that eventually we can determine the set of images that contain matching faces.
  for hash_bytes in redisHashToFaceRec.scan_iter():
    hash = hash_bytes.decode("utf-8")  # hashes below are strings
    if hash == img_hash:
      continue

    face_recs_pickled = redisHashToFaceRec.smembers(hash)
    face_recs = [pickle.loads(f) for f in face_recs_pickled]

    for unknown_face in unknown_face_encodings:
      match_results = face_recognition.compare_faces(face_recs, unknown_face)
      print(f'results: {match_results}')
      if any(match_results):
        _log(ch, "worker", f" [x] Found Match: {img_name}, img_hash: {img_hash}, existing hash: {hash}")
        redisHashToHashSet.sadd(img_hash, hash)
        redisHashToHashSet.sadd(hash, img_hash)


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
redisHashToFaceRec = redis.Redis(host=redisHost, db=3)
redisHashToHashSet = redis.Redis(host=redisHost, db=4)

configureRabbitMqReceiver()