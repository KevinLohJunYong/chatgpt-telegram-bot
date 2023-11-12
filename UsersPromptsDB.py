import redis
import constants as c

class UsersPromptsDB:
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add_user_prompt(self,user_id,prompt):
        user_id_str = str(user_id)
        if not self.redis.exists(user_id_str) or self.redis.type(user_id_str).decode('utf-8') != 'list':
            self.redis.delete(user_id_str)
            self.redis.rpush(user_id_str, "")
        self.redis.rpush(user_id_str,prompt)

    def get_conversation_context(self,user_id):
        self.redis.ltrim(user_id, -c.CONVERSATION_CONTEXT_SIZE, -1)
        user_list = self.redis.lrange(user_id, 0, -1)
        user_list = [item.decode('utf-8') for item in user_list]
        return user_list