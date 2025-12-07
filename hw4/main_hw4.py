from pymongo import MongoClient, ASCENDING
import random

# Подключаемся надо только вначале докер поднять.
client = MongoClient()
db = client["simple_db"]
users = db.users

# Тут удаляем индексы и оздаем по новой
users.drop()
users.create_index("city")
users.create_index([("status", ASCENDING), ("age", ASCENDING)])


data = [
    {
        "name": f"User{i}",
        "age": random.randint(20, 50),
        "city": random.choice(["Moscow", "SPb", "Kazan"]),
        "status": random.choice(["active", "inactive"]),
        "profile": {
            "skill": random.choice(["Python", "Java", "JS"]),
            "level": random.randint(1, 5)
        }
    }
    for i in range(30)
]
users.insert_many(data)
print("Данные добавлены")


class UserManager:
    def __init__(self, collection):
        self.col = collection

    def get_active_by_city(self, city):
        return list(self.col.find({"city": city, "status": "active"}))

    def update_status(self, name, status):
        self.col.update_one({"name": name}, {"$set": {"status": status}})


print("\nАгрегация 1: Статистика по городам")
result1 = users.aggregate([
    {"$group": {
        "_id": "$city",
        "count": {"$sum": 1},
        "avg_age": {"$avg": "$age"}
    }}
])
for r in result1:
    print(f"{r['_id']}: {r['count']} users, avg age {r['avg_age']:.1f}")

print("\nАгрегация 2: Активные пользователи по городу (использует индекс)")
result2 = users.aggregate([
    {"$match": {"status": "active"}},  # Использует индекс
    {"$group": {
        "_id": "$city",
        "active_users": {"$sum": 1}
    }}
])
for r in result2:
    print(f"{r['_id']}: {r['active_users']} active users")

if __name__ == "__main__":
    manager = UserManager(users)
    moscow_active = manager.get_active_by_city("Moscow")
    print(f"\nАктивных в Москве: {len(moscow_active)}")
