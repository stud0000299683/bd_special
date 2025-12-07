import redis
import time

r = redis.Redis()
channel = "news"

for i in range(5):
    message = f"Новость #{i+1}"
    r.publish(channel, message)
    print(f"📤 Отправлено: {message}")
    time.sleep(1)
