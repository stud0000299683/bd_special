import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError

fake = Faker()


class TestUserRepositoryWithFaker:
    """Тесты с использованием Faker для генерации данных"""

    @pytest.fixture
    def fake_user_data(self):
        """Генерация фейковых данных пользователя"""
        return {
            "email": fake.email(),
            "username": fake.user_name(),
            "full_name": fake.name()
        }

    def test_create_multiple_users(self, user_repository):
        """Создание нескольких пользователей с разными данными"""
        # Arrange
        users_data = [
            {
                "email": fake.unique.email(),
                "username": fake.unique.user_name(),
                "full_name": fake.name()
            }
            for _ in range(5)
        ]

        created_users = []

        # Act
        for data in users_data:
            user = user_repository.create(**data)
            created_users.append(user)

        # Assert
        assert len(created_users) == 5

        # Проверяем, что все пользователи созданы
        all_users = user_repository.get_all()
        assert len(all_users) == 5

    def test_unique_constraints_with_faker(self, user_repository, fake_user_data):
        """Тест уникальных ограничений с сгенерированными данными"""
        # Arrange
        user_repository.create(**fake_user_data)

        # Act & Assert - попытка создать пользователя с тем же email
        with pytest.raises(IntegrityError):
            user_repository.create(
                email=fake_user_data["email"],  # Дубликат
                username="different_username",
                full_name="Different Name"
            )
