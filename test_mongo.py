from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['test_database']


users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']


def clear_collections():
    """Функция для очистки данных (коллекций)"""
    users_collection.delete_many({})
    products_collection.delete_many({})
    orders_collection.delete_many({})
    print("Коллекции очищены\n")


def create_users():
    """Функция для создания пользователей """
    users = [
        {
            'name': 'Иванов Иван',
            'email': 'Ivanov.I@example.com',
            'age': 30,
            'city': 'Брянск',
            'created_at': datetime.now()
        },
        {
            'name': 'Петр Петров',
            'email': 'petrov.p@example.com',
            'age': 25,
            'city': 'Новосибирск',
            'created_at': datetime.now()
        },
        {
            'name': 'Сидоров Сергей',
            'email': 'Sidorov.SS@example.com',
            'age': 35,
            'city': 'Москва',
            'created_at': datetime.now()
        }
    ]

    result = users_collection.insert_many(users)
    print(f"Создано пользователей: {len(result.inserted_ids)}")
    for user_id in result.inserted_ids:
        print(f"  - ID пользователя: {user_id}")


def read_data():
    """Функция чтения данных"""
    users = users_collection.find()
    for user in users:
        print(f"ID: {user['_id']}, Name: {user['name']}, Email: {user['email']}, City: {user['city']}")


def update_operations():
    """Ф-ия обновления данных"""
    result = users_collection.update_one(
        {'name': 'Сидоров Сергей'},
        {'$set': {'age': 36, 'city': 'Сочи'}}
    )
    print(f"Обновлено пользователей: {result.modified_count}")


def delete_operations():
    """Ф-ия удаления"""
    result = users_collection.delete_one({'name': 'Иванов Иван'})
    print(f"Удалено пользователей: {result.deleted_count}")


if __name__ == "__main__":
    try:
        clear_collections()
        create_users()
        read_data()
        update_operations()
        delete_operations()
        read_data()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        client.close()
        print("\nСоединение с MongoDB закрыто")
