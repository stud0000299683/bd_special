from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, text, insert, select, update, delete
from sqlalchemy.exc import DataError, SQLAlchemyError
from typing import Optional, Dict, Any, List
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_url: str, default_db: str = "postgres"):
        self.default_db_url = db_url.replace('/test', f'/{default_db}')
        self.db_url = db_url
        self.engine = None
        self.metadata = MetaData()

        # Определение таблицы
        self.users = Table('users', self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('name', String(100), nullable=False),
                           Column('email', String(255), unique=True),
                           Column('age', Integer)
                           )

    def create_db(self, db_name: str) -> bool:
        """Создает базу данных если она не существует"""
        try:
            server_engine = create_engine(
                self.default_db_url,
                isolation_level="AUTOCOMMIT"
            )

            with server_engine.connect() as conn:
                # Проверяем существование базы данных
                check_query = text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                )
                result = conn.execute(check_query, {'db_name': db_name})
                exists = result.first() is not None

                if exists:
                    logger.info(f'Database {db_name} already exists')
                    return True

                # Создаем базу данных
                create_query = text(f'CREATE DATABASE {db_name}')
                conn.execute(create_query)
                logger.info(f'Database {db_name} created successfully')
                return True

        except SQLAlchemyError as e:
            logger.error(f"Error creating database {db_name}: {e}")
            return False
        finally:
            if 'server_engine' in locals():
                server_engine.dispose()

    def get_engine(self):
        """Ленивая инициализация engine"""
        if self.engine is None:
            self.engine = create_engine(self.db_url)
        return self.engine

    def create_tables(self) -> bool:
        """Создает все таблицы"""
        try:
            engine = self.get_engine()
            self.metadata.create_all(engine)
            logger.info('All tables created successfully')
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            return False

    def create_user(self, name: str, email: str, age: int) -> Optional[int]:
        """Создает нового пользователя и возвращает его ID"""
        try:
            insert_query = (
                insert(self.users)
                .values(name=name, email=email, age=age)
                .returning(self.users.c.id)
            )

            with self.get_engine().connect() as conn:
                result = conn.execute(insert_query)
                conn.commit()
                user_id = result.scalar()
                logger.info(f'Created user with ID: {user_id}')
                return user_id

        except DataError as e:
            logger.error(f'Data error: {e}. Check input data types.')
        except SQLAlchemyError as e:
            logger.error(f'Database error creating user: {e}')
        return None

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по ID"""
        try:
            select_query = select(self.users).where(self.users.c.id == user_id)

            with self.get_engine().connect() as conn:
                result = conn.execute(select_query)
                user_data = result.mappings().first()

                if user_data:
                    logger.info(f'Found user: {dict(user_data)}')
                    return dict(user_data)
                else:
                    logger.warning(f'User with ID {user_id} not found')
                    return None

        except SQLAlchemyError as e:
            logger.error(f'Error retrieving user {user_id}: {e}')
            return None

    def get_users_by_age(self, min_age: int = None, max_age: int = None) -> List[Dict[str, Any]]:
        """Получает пользователей по возрастному диапазону"""
        try:
            query = select(self.users)

            if min_age is not None:
                query = query.where(self.users.c.age >= min_age)
            if max_age is not None:
                query = query.where(self.users.c.age <= max_age)

            with self.get_engine().connect() as conn:
                result = conn.execute(query)
                users = [dict(row) for row in result.mappings().all()]
                logger.info(f'Found {len(users)} users')
                return users

        except SQLAlchemyError as e:
            logger.error(f'Error retrieving users: {e}')
            return []

    def update_user_email(self, user_id: int, email: str) -> bool:
        """Обновляет email пользователя"""
        try:
            update_query = (
                update(self.users)
                .where(self.users.c.id == user_id)
                .values(email=email)
            )

            with self.get_engine().connect() as conn:
                result = conn.execute(update_query)
                conn.commit()

                if result.rowcount > 0:
                    logger.info(f'Updated email for user {user_id}')
                    return True
                else:
                    logger.warning(f'User {user_id} not found for update')
                    return False

        except SQLAlchemyError as e:
            logger.error(f'Error updating user {user_id}: {e}')
            return False

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновляет любые поля пользователя"""
        try:
            if not kwargs:
                logger.warning('No fields to update')
                return False

            update_query = (
                update(self.users)
                .where(self.users.c.id == user_id)
                .values(**kwargs)
            )

            with self.get_engine().connect() as conn:
                result = conn.execute(update_query)
                conn.commit()

                if result.rowcount > 0:
                    logger.info(f'Updated user {user_id} with fields: {kwargs}')
                    return True
                else:
                    logger.warning(f'User {user_id} not found for update')
                    return False

        except SQLAlchemyError as e:
            logger.error(f'Error updating user {user_id}: {e}')
            return False

    def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя по ID"""
        try:
            delete_query = delete(self.users).where(self.users.c.id == user_id)

            with self.get_engine().connect() as conn:
                result = conn.execute(delete_query)
                conn.commit()

                if result.rowcount > 0:
                    logger.info(f'Deleted user {user_id}')
                    return True
                else:
                    logger.warning(f'User {user_id} not found for deletion')
                    return False

        except SQLAlchemyError as e:
            logger.error(f'Error deleting user {user_id}: {e}')
            return False

    def user_exists(self, user_id: int) -> bool:
        """Проверяет существование пользователя"""
        try:
            query = select(self.users.c.id).where(self.users.c.id == user_id)

            with self.get_engine().connect() as conn:
                result = conn.execute(query)
                return result.first() is not None

        except SQLAlchemyError as e:
            logger.error(f'Error checking user existence: {e}')
            return False

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.engine:
            self.engine.dispose()
            logger.info('Database connection closed')


if __name__ == '__main__':
    # Конфигурация
    DB_URL = 'postgresql://postgres:pwd@localhost:5432/test'

    db_manager = DatabaseManager(DB_URL)

    try:
        if db_manager.create_db('test'):
            db_manager.create_tables()

        user_id = db_manager.create_user('Petr', 'petr@mail.ru', 25)

        if user_id:
            # Получаем пользователя
            user = db_manager.get_user(user_id)
            print(f"User: {user}")
            db_manager.update_user_email(user_id, 'new_petr@mail.ru')
            young_users = db_manager.get_users_by_age(max_age=30)
            print(f"Young users: {young_users}")
            db_manager.delete_user(user_id)
    finally:
        db_manager.close()