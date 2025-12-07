import redis

r = redis.Redis()
queue = "tasks"

for i in range(5):
    task = f"Задача {i+1}"
    r.rpush(queue, task)
    print(f"Добавлено: {task}")
