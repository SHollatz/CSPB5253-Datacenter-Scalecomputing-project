##
from flask import Flask, request, Response
import codecs
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests
from PIL import Image

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("rabbitMQHost: ", rabbitMQHost)

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

# Initialize the Flask application
app = Flask(__name__)


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

# route http posts to this method
@app.route('/')
def root():
    return 'Welcome'

@app.route('/scan/image/<filename>', methods=['POST'])
def scanImage(filename=None):
    return _scanImageInternal('/scan/image', filename, request.data)

@app.route('/scan/url', methods=['POST'])
def scanURL():
    url = jsonpickle.decode(request.data)['url']
    r = requests.get(url, allow_redirects=True)
    img = r.content
    return _scanImageInternal('/scan/url', url, img)

@app.route('/match/<img_hash>', methods=['GET'])
def matchHash(img_hash):
    all_names = set()
    matching_face = redisHashToPred.smembers(img_hash)
    if (matching_face):
        matched_name = redisHashToName.smembers(img_hash)
        all_names.update(matched_name)

    if all_names:
        all_names_list = sorted(list(all_names))
        all_names_list = [n.decode('utf8') for n in all_names_list]
    else:
        all_names_list = []

    response = {
        'matched_names': all_names_list
    }
    # print(f'response: {response}')

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

def _scanImageInternal(log_prefix, filename, img_data):
    channel = _getChannel()
    _log(channel, f"rest-server.py: {log_prefix}", "begin")
    
    # convert the data to a PIL image type so we can extract dimensions
    ioBuffer = io.BytesIO(img_data)
    img = Image.open(ioBuffer)
    img_hash = hashlib.sha256(img.tobytes()).hexdigest()

    body = {
        "hash": img_hash,
        "filename": filename,
        "img": img
    }
    body_pickled = codecs.encode(pickle.dumps(body), "base64").decode()
    err = channel.basic_publish(
        exchange='',
        routing_key='toWorker',
        body=body_pickled,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    if (err):
        print(f"ERROR in rest-server: {log_prefix}: ", err)
    # print(" [x] Sent %r" % response_pickled)

    _log(channel, f"rest-server.py: {log_prefix}", f"processed image {filename}")
    channel.close()

    # build a response dict to send back to client
    response = {
        "hash": img_hash,
        "filename": filename,
    }
    # print("response: ", response)
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# Initialize Redis
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToPred = redis.Redis(host=redisHost, db=3)

# start flask app
app.run(host="0.0.0.0", port=5000)