import redis
import time

r = redis.Redis()
queue = "tasks"

print("👷 Обработчик запущен")
while True:
    task = r.blpop(queue, timeout=0)
    if task:
        print(f"✅ Выполнено: {task[1]}")
        time.sleep(1)
  