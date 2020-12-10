import os
import redis

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisNameToHash = redis.Redis(host=redisHost, db=1)
redisHashToName = redis.Redis(host=redisHost, db=2)
redisHashToPred = redis.Redis(host=redisHost, db=3)

def printInfo(context):
  for db in [redisNameToHash, redisHashToName, redisHashToPred]:
    print(f'{context}: SIZE: {db.dbsize()}; DB: {db}')

printInfo('before')
redisHashToPred.flushall()
printInfo(' after')