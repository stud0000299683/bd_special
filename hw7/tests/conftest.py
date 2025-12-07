import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.user import Base

# Тестовая БД в памяти
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def engine():
    """Движок БД для тестов"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    """Сессия БД с автооткатом"""
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def user_repository(db_session):
    """Репозиторий для тестов"""
    from ..repositories.user_repository import UserRepository
    return UserRepository(db_session)


@pytest.fixture
def sample_user_data():
    """Тестовые данные пользователя"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User"
    }