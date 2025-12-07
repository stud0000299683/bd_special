import redis

r = redis.Redis()
pubsub = r.pubsub()
pubsub.subscribe("news")

print("Слушаем канал 'news'...")
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Получено: {message['data']}")
