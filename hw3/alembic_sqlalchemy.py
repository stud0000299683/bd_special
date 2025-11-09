from sqlalchemy import Column, Integer, String, create_engine, MetaData, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy import update, select
from typing import List, Optional

metadata = MetaData()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    age = Column(Integer)

    # one-to-many
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    # many-to-one
    author = relationship("User", back_populates="posts")


engine = create_engine('postgresql://postgres:pwd@localhost:5432/test')
session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

from contextlib import contextmanager


@contextmanager
def get_session():
    session = session_local()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f'Error {e}')
        raise
    finally:
        session.close()


def create_user(age: int, name: str, email: str) -> int:
    """Создает пользователя и возвращает его ID"""
    new_user = User(
        name=name,
        email=email,
        age=age,
    )

    with get_session() as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user_id = new_user.id
        print(f"Created user: {name} with ID: {user_id}")
        return user_id


def create_post(title: str, content: str, user_id: int) -> int:
    """Создает пост и возвращает его ID"""
    new_post = Post(
        title=title,
        content=content,
        user_id=user_id,
    )

    with get_session() as session:
        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        post_id = new_post.id
        print(f"Created post: '{title}' for user ID: {user_id}")
        return post_id


def create_multiple_posts(list_posts: List[Post]) -> List[int]:
    """Создает несколько постов и возвращает список их ID"""
    with get_session() as session:
        session.add_all(list_posts)
        session.commit()
        post_ids = []
        for post in list_posts:
            session.refresh(post)
            post_ids.append(post.id)
        print(f'Created {len(list_posts)} posts')
        return post_ids


def delete_user(user_id: int) -> bool:
    """Удаляет пользователя по ID"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            print(f'Deleted user {user_id}')
            return True
        else:
            print(f'User not found {user_id}')
            return False


def get_user(user_id: int) -> Optional[User]:
    """Получает пользователя по ID"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            print(f"Found user: ID={user.id}, Name={user.name}, Email={user.email}, Age={user.age}")
            print(f"User has {len(user.posts)} posts")
            return user
        else:
            print(f"User with ID {user_id} not found")
            return None


def update_user(user_id: int, name: Optional[str] = None, email: Optional[str] = None,
                age: Optional[int] = None) -> bool:
    """Обновляет данные пользователя"""
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            print(f"User with ID {user_id} not found")
            return False

        update_data = {}
        if name is not None:
            update_data['name'] = name
        if email is not None:
            update_data['email'] = email
        if age is not None:
            update_data['age'] = age

        if update_data:
            for key, value in update_data.items():
                setattr(user, key, value)
            session.commit()
            print(f"Updated user {user_id} with: {update_data}")
            return True
        else:
            print("No data provided for update")
            return False


def get_post(post_id: int) -> Optional[Post]:
    """Получает пост по ID"""
    with get_session() as session:
        post = session.get(Post, post_id)
        if post:
            print(f"Found post: ID={post.id}, Title='{post.title}', Author ID={post.user_id}")
            return post
        else:
            print(f"Post with ID {post_id} not found")
            return None


def update_post(post_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
    """Обновляет данные поста"""
    with get_session() as session:
        post = session.get(Post, post_id)
        if not post:
            print(f"Post with ID {post_id} not found")
            return False

        update_data = {}
        if title is not None:
            update_data['title'] = title
        if content is not None:
            update_data['content'] = content

        if update_data:
            for key, value in update_data.items():
                setattr(post, key, value)
            session.commit()
            print(f"Updated post {post_id} with: {update_data}")
            return True
        else:
            print("No data provided for update")
            return False


def delete_post(post_id: int) -> bool:
    """Удаляет пост по ID"""
    with get_session() as session:
        post = session.get(Post, post_id)
        if post:
            session.delete(post)
            session.commit()
            print(f'Deleted post {post_id}')
            return True
        else:
            print(f'Post not found {post_id}')
            return False


def get_user_with_posts(user_id: int) -> Optional[dict]:
    """Получает пользователя вместе со всеми его постами"""
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age,
                'posts': [
                    {
                        'id': post.id,
                        'title': post.title,
                        'content': post.content
                    } for post in user.posts
                ]
            }
            print(f"User: {user.name} (ID: {user.id})")
            print(f"Email: {user.email}, Age: {user.age}")
            print("Posts:")
            if user.posts:
                for post in user.posts:
                    print(f"  - {post.title}: {post.content}")
            else:
                print("  No posts")
            return user_data
        else:
            print(f"User with ID {user_id} not found")
            return None


def get_all_users() -> List[dict]:
    """Получает всех пользователей"""
    with get_session() as session:
        users = session.query(User).all()
        print(f"Found {len(users)} users")
        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age,
                'post_count': len(user.posts)
            }
            users_data.append(user_data)
            print(f"  - {user.name} (ID: {user.id}), Posts: {len(user.posts)}")
        return users_data


def get_posts_by_user(user_id: int) -> List[dict]:
    """Получает все посты пользователя"""
    with get_session() as session:
        posts = session.query(Post).filter(Post.user_id == user_id).all()
        print(f"Found {len(posts)} posts for user {user_id}")
        posts_data = []
        for post in posts:
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content
            }
            posts_data.append(post_data)
            print(f"  - {post.title}: {post.content}")
        return posts_data


def search_users_by_name(name_pattern: str) -> List[dict]:
    """Ищет пользователей по шаблону имени"""
    with get_session() as session:
        users = session.query(User).filter(User.name.ilike(f"%{name_pattern}%")).all()
        print(f"Found {len(users)} users matching '{name_pattern}'")
        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age
            }
            users_data.append(user_data)
            print(f"  - {user.name} (ID: {user.id}, Email: {user.email})")
        return users_data


def create_user_with_posts(user_data: dict, posts_data: List[dict]) -> int:
    """Создает пользователя и его посты в одной транзакции"""
    with get_session() as session:
        # Создаем пользователя
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            age=user_data['age']
        )
        session.add(user)
        session.flush()  # Получаем ID пользователя без коммита

        # Создаем посты
        for post_data in posts_data:
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                user_id=user.id
            )
            session.add(post)

        session.commit()
        session.refresh(user)
        print(f"Created user {user.name} with {len(posts_data)} posts")
        return user.id


if __name__ == '__main__':
    # Создаем таблицы
    Base.metadata.create_all(engine)

    # Пример 1: Создание пользователя и постов по отдельности
    user_id = create_user(23, 'John', 'john@mail.ru')
    create_post('First Post', 'This is my first post', user_id)
    create_post('Second Post', 'This is my second post', user_id)

    # Пример 2: Создание пользователя с постами в одной транзакции
    user_data = {
        'name': 'Alice',
        'email': 'alice@mail.ru',
        'age': 25
    }
    posts_data = [
        {'title': 'Alice Post 1', 'content': 'Content 1'},
        {'title': 'Alice Post 2', 'content': 'Content 2'}
    ]
    alice_id = create_user_with_posts(user_data, posts_data)

    # Другие операции
    get_user_with_posts(user_id)
    get_all_users()
    search_users_by_name('John')
    get_posts_by_user(user_id)

    # Обновления
    update_user(user_id, name='John Updated', age=24)
    update_post(1, title='Updated Title', content='Updated content')