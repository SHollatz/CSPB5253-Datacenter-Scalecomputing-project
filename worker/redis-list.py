import os
import pickle
import redis

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToPred = redis.Redis(host=redisHost, db=3)

print()
print('--- redisHashToFile-----------------------------------------------------------')
for key in redisHashToName.scan_iter():
  members = redisHashToName.smembers(key)
  print(f'{key} names: {members}')
print()
print('--- redisFileToHash-----------------------------------------------------------')
for key in redisNameToHash.scan_iter():
  value = redisNameToHash.get(key)
  print(f'{key} hash: {value}')
print()
print('--- redisHashToPred -----------------------------------------------------------')
for key in redisHashToPred.scan_iter():
  class_name = redisHashToPred.get(key)
  print(f'{key} class: {class_name}')
  # for member in redisHashToFaceRec.smembers(key):
  #   print(key, pickle.loads(member))
