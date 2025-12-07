import redis
import time

# Подключаемся
r = redis.Redis(host='localhost', port=6379, db=0)

# Сохраняем данные с TTL (30 секунд)
r.setex("user:100", 30, "Иван Иванов")
print("✅ Данные сохранены на 30 сек")

# Получаем данные
data = r.get("user:100")
print(f"Данные: {data}")

# Проверяем TTL
ttl = r.ttl("user:100")
print(f"Осталось секунд: {ttl}")
