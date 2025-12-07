import pytest
from sqlalchemy.exc import IntegrityError
from ..models.user import User


class TestUserRepository:
    """Основные тесты CRUD для пользователей"""

    # ПОЗИТИВНЫЕ ТЕСТЫ

    def test_create_user_success(self, user_repository, sample_user_data):
        """Успешное создание пользователя"""
        # Act
        user = user_repository.create(**sample_user_data)

        # Assert
        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]

    def test_get_user_by_id_success(self, user_repository, sample_user_data):
        """Успешное получение пользователя по ID"""
        # Arrange
        created_user = user_repository.create(**sample_user_data)

        # Act
        found_user = user_repository.get_by_id(created_user.id)

        # Assert
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    def test_get_user_by_email_success(self, user_repository, sample_user_data):
        """Успешное получение пользователя по email"""
        # Arrange
        created_user = user_repository.create(**sample_user_data)

        # Act
        found_user = user_repository.get_by_email(sample_user_data["email"])

        # Assert
        assert found_user is not None
        assert found_user.email == sample_user_data["email"]

    def test_get_all_users_success(self, user_repository):
        """Успешное получение всех пользователей"""
        # Arrange
        user1 = user_repository.create(
            email="user1@example.com",
            username="user1",
            full_name="User One"
        )
        user2 = user_repository.create(
            email="user2@example.com",
            username="user2",
            full_name="User Two"
        )

        # Act
        all_users = user_repository.get_all()

        # Assert
        assert len(all_users) == 2
        assert user1 in all_users
        assert user2 in all_users

    def test_update_user_success(self, user_repository, sample_user_data):
        """Успешное обновление пользователя"""
        # Arrange
        user = user_repository.create(**sample_user_data)
        new_name = "Updated Name"

        # Act
        updated_user = user_repository.update(user.id, new_name)

        # Assert
        assert updated_user is not None
        assert updated_user.full_name == new_name

    def test_delete_user_success(self, user_repository, sample_user_data):
        """Успешное удаление пользователя"""
        # Arrange
        user = user_repository.create(**sample_user_data)

        # Act
        delete_result = user_repository.delete(user.id)

        # Assert
        assert delete_result is True
        deleted_user = user_repository.get_by_id(user.id)
        assert deleted_user is None

    # НЕГАТИВНЫЕ ТЕСТЫ

    def test_create_user_duplicate_email(self, user_repository, sample_user_data):
        """Попытка создания пользователя с существующим email"""
        # Arrange
        user_repository.create(**sample_user_data)

        # Act & Assert
        with pytest.raises(IntegrityError):
            user_repository.create(
                email=sample_user_data["email"],  # Дубликат email
                username="anotheruser",
                full_name="Another User"
            )

    def test_get_user_by_id_not_found(self, user_repository):
        """Попытка получения несуществующего пользователя"""
        # Act
        user = user_repository.get_by_id(999)

        # Assert
        assert user is None

    def test_update_user_not_found(self, user_repository):
        """Попытка обновления несуществующего пользователя"""
        # Act
        result = user_repository.update(999, "New Name")

        # Assert
        assert result is None

    def test_delete_user_not_found(self, user_repository):
        """Попытка удаления несуществующего пользователя"""
        # Act
        result = user_repository.delete(999)

        # Assert
        assert result is False