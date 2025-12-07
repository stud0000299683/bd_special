import redis
import time
import threading

r = redis.Redis()


def caching_example():
    """Кеширование с TTL"""
    print("\n1. КЕШИРОВАНИЕ:")
    r.setex("cache_key", 10, "секретные данные")
    print(f"Кеш создан: {r.get('cache_key')}")
    print(f"TTL: {r.ttl('cache_key')} сек")


def pubsub_example():
    print("\n2. PUB/SUB:")

    # Запускаем подписчика в потоке
    def subscriber():
        pubsub = r.pubsub()
        pubsub.subscribe("test_channel")
        for msg in pubsub.listen():
            if msg['type'] == 'message':
                print(f"Получено: {msg['data']}")
                break

    thread = threading.Thread(target=subscriber)
    thread.start()

    time.sleep(0.5)  # Даем время подписаться
    r.publish("test_channel", "Привет от Redis!")

    thread.join()


def queue_example():
    print("\n3. ОЧЕРЕДЬ ЗАДАЧ:")

    # Добавляем задачи
    for i in range(3):
        r.rpush("task_queue", f"Task-{i + 1}")

    # Обрабатываем задачи
    for i in range(3):
        task = r.blpop("task_queue", timeout=1)
        if task:
            print(f"Обработано: {task[1]}")


if __name__ == "__main__":
    caching_example()
    pubsub_example()
    queue_example()

    r.delete("cache_key", "task_queue")
    print("\n✅ Все примеры выполнены!")
