import psycopg2
from sqlalchemy import create_engine, text
import getpass

# Конфигурация
DB_CONFIG = {
    "host": "localhost",
    "database": "test_db",
    "user": "postgres",
    "password": getpass.getpass("Пароль БД: ")
}


def setup_db():
    """Настройка тестовой БД"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            email VARCHAR(100),
            is_admin BOOLEAN DEFAULT false
        );
        INSERT INTO users (username, email, is_admin) VALUES
        ('admin', 'admin@test.com', true),
        ('user1', 'user1@test.com', false);
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("[✓] БД создана")


# ==================== УЯЗВИМЫЕ МЕТОДЫ ====================

def vulnerable_auth(username, password):
    """Уязвимая авторизация"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ⚠️ SQL-инъекция через конкатенацию
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"[Уязвимый запрос]: {query}")

    cur.execute(query)
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


def vulnerable_search(search):
    """Уязвимый поиск"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = f"SELECT * FROM users WHERE username LIKE '%{search}%'"
    print(f"[Уязвимый поиск]: {query}")

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()
    return results


# ==================== ЗАЩИЩЕННЫЕ МЕТОДЫ ====================

def secure_auth_psycopg2(username):
    """Защита через параметризацию psycopg2"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = "SELECT * FROM users WHERE username = %s"
    print(f"[Psycopg2]: {query}")
    print(f"   Параметр: {username}")

    cur.execute(query, (username,))
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


def secure_auth_sqlalchemy(username):
    """Защита через SQLAlchemy"""
    conn_str = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    engine = create_engine(conn_str)

    query = text("SELECT * FROM users WHERE username = :username")
    print(f"[SQLAlchemy]: {query}")
    print(f"   Параметр: username = {username}")

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username}).fetchone()

    return result


def secure_dynamic_query(filters):
    """Динамический безопасный запрос"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if 'username' in filters:
        query += " AND username = %s"
        params.append(filters['username'])

    if 'is_admin' in filters:
        query += " AND is_admin = %s"
        params.append(filters['is_admin'])

    print(f"[Динамический запрос]: {query}")
    print(f"   Параметры: {params}")

    cur.execute(query, params)
    results = cur.fetchall()

    cur.close()
    conn.close()
    return results


# ==================== ДЕМОНСТРАЦИЯ ====================

def demonstrate_injections():
    """Демонстрация инъекций"""
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ SQL-ИНЪЕКЦИЙ")
    print("=" * 50)

    # 1. Байпас авторизации
    print("\n1. Байпас авторизации:")
    print("   Ввод: admin' --")
    result = vulnerable_auth("admin' --", "")
    print(f"   Результат: {'УСПЕХ' if result else 'НЕТ'}")

    # 2. Извлечение всех данных
    print("\n2. Извлечение всех данных:")
    print("   Ввод: ' UNION SELECT * FROM users --")
    result = vulnerable_auth("' UNION SELECT * FROM users --", "")
    print(f"   Результат: {len(result) if result else 0} столбцов")

    # 3. Инъекция в LIKE
    print("\n3. Инъекция в поиск:")
    print("   Ввод: %' UNION SELECT * FROM users --")
    results = vulnerable_search("%' UNION SELECT * FROM users --")
    print(f"   Найдено: {len(results)} записей")


def demonstrate_protection():
    """Демонстрация защиты"""
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ")
    print("=" * 50)

    test_cases = [
        ("admin' --", "Байпас"),
        ("' UNION SELECT * FROM users --", "UNION"),
        ("'; DROP TABLE users; --", "Удаление"),
    ]

    for input_data, name in test_cases:
        print(f"\nТест: {name}")
        print(f"Ввод: {input_data}")

        # Пробуем пройти защиту
        result = secure_auth_psycopg2(input_data)
        print(f"Psycopg2: {'Заблокировано' if not result else 'УСПЕХ'}")

        result = secure_auth_sqlalchemy(input_data)
        print(f"SQLAlchemy: {'Заблокировано' if not result else 'УСПЕХ'}")


def main():
    """Главная функция"""
    try:
        setup_db()

        print("\n" + "=" * 50)
        print("БЕЗОПАСНАЯ ДЕМОНСТРАЦИЯ")
        print("=" * 50)

        # Показываем примеры, но не выполняем реальные инъекции
        print("\nПримеры вредоносного ввода:")
        print("   1. Байпас: admin' --")
        print("   2. UNION: ' UNION SELECT * FROM users --")
        print("   3. Удаление: '; DROP TABLE users; --")

        print("\n🛡️ Защищенные запросы:")

        # Тест нормального ввода
        print("\n1. Нормальный запрос:")
        secure_auth_psycopg2("admin")

        # Тест динамического запроса
        print("\n2. Динамический фильтр:")
        secure_dynamic_query({"username": "admin", "is_admin": True})

        print("\n" + "=" * 50)
        print("ВЫВОД: Всегда используйте параметризацию!")
        print("       Никогда не конкатенируйте пользовательский ввод.")

    except Exception as e:
        print(f"\n[Ошибка]: {e}")


if __name__ == "__main__":
    main()