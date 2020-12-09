import os
import redis

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToFaceRec = redis.Redis(host=redisHost, db=3)
redisHashToHashSet = redis.Redis(host=redisHost, db=4)

def printInfo(context):
  for db in [redisNameToHash, redisHashToName, redisHashToFaceRec, redisHashToHashSet]:
    print(f'{context}: SIZE: {db.dbsize()}; DB: {db}')

printInfo('before')
redisHashToFaceRec.flushall()
printInfo(' after')