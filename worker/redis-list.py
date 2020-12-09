import os
import pickle
import redis

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToFaceRec = redis.Redis(host=redisHost, db=3)
redisHashToHashSet = redis.Redis(host=redisHost, db=4)
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
print('--- redisHashToFaceRec -----------------------------------------------------------')
for key in redisHashToFaceRec.scan_iter():
  members = redisHashToFaceRec.smembers(key)
  print(f'{key} faces: {len(members)}')
  # for member in redisHashToFaceRec.smembers(key):
  #   print(key, pickle.loads(member))

print()
print('--- redisHashToHashSet -----------------------------------------------------------')
for key in redisHashToHashSet.scan_iter():
  members = redisHashToHashSet.smembers(key)
  print(f'{key} hashes: {members}')