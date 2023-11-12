import redis
import time
import constants as c

limit = c.RATE_LIMIT_NUMBER
window = c.RATE_LIMIT_WINDOW

class RateLimiterDB:
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def is_user_rate_limited(self,key):
        key = f"rate limiting key: {key}"
        current_time = int(time.time())
        window_start = current_time - window
        print(f"key: {key}")
        # Check if the key exists and is a zset
        if not self.redis.exists(key) or self.redis.type(key).decode('utf-8') != 'zset':
            # Initialize the key as an empty zset if it doesn't exist or isn't a zset
            self.redis.zadd(key, {current_time: current_time})
            return False  # Assuming a fresh start means not rate-limited
        num_requests_made = self.redis.zcount(key, window_start, current_time)
        print(num_requests_made)

        if num_requests_made < limit:
            print("user is not rate limited")
            self.redis.zadd(key, {current_time: current_time})
            self.redis.zremrangebyscore(key, '-inf', window_start)
            return False

        else:
            print("user is rate limited")
            return True

    def print_redis_contents(self):
        keys = self.redis.keys('*')
        for key in keys:
            key_type = self.redis.type(key).decode('utf-8')
            print(f"Key: {key.decode('utf-8')}, Type: {key_type}", end='')
            if key_type == 'string':
                value = self.redis.get(key).decode('utf-8')
                print(f", Value: {value}")
            elif key_type == 'list':
                value = self.redis.lrange(key, 0, -1)
                print(f", Values: {[v.decode('utf-8') for v in value]}")
            elif key_type == 'set':
                value = self.redis.smembers(key)
                print(f", Values: {[v.decode('utf-8') for v in value]}")
            elif key_type == 'zset':
                value = self.redis.zrange(key, 0, -1, withscores=True)
                print(f", Values: {[(v[0].decode('utf-8'), v[1]) for v in value]}")
            elif key_type == 'hash':
                value = self.redis.hgetall(key)
                print(f", Values: {{key.decode('utf-8'): val.decode('utf-8') for key, val in value.items()}}")
            else:
                print(", Unknown or unsupported type")


