from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from models.user import User
from models.task import Task
import logging
from sqlalchemy.future import select
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./taskmanager.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._engine = create_async_engine(DATABASE_URL, echo=True)
            cls._instance._async_session = sessionmaker(cls._instance._engine, class_=AsyncSession, expire_on_commit=False)
        return cls._instance

    @property
    def engine(self):
        return self._engine

    @property
    def async_session(self):
        return self._async_session

    async def init_models(self):
        async with self.engine.begin() as conn:
            def check_table_exists(conn):
                inspector = inspect(conn)
                return inspector.has_table("users")
            
            table_exists = await conn.run_sync(check_table_exists)
            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Таблицы успешно созданы.")
            else:
                logger.info("Таблицы уже существуют. Пропускаем создание.")

    async def check_db_connection(self):
        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
                logger.info("Подключение к базе данных успешно установлено.")
        except Exception as e:
            logger.error(f"Ошибка при проверке подключения к базе данных: {e}")
            raise

    async def test_async_session(self):
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                logger.info(f"Тестирование асинхронной сессии: {result.scalar()}")
        except Exception as e:
            logger.error(f"Ошибка при тестировании асинхронной сессии: {e}")
            raise

    async def generate_unique_slug(self, session, base_slug):
        counter = 1
        while True:
            slug = f"{base_slug}-{uuid.uuid4().hex[:8]}" if counter > 1 else base_slug
            result = await session.execute(select(User).where(User.slug == slug))
            if not result.scalar_one_or_none():
                return slug
            counter += 1

    async def generate_unique_username(self, session, base_username):
        counter = 1
        while True:
            username = f"{base_username}-{uuid.uuid4().hex[:8]}" if counter > 1 else base_username
            result = await session.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                return username
            counter += 1

    async def test_data_operations(self):
        async with self.async_session() as session:
            try:
                # Создание пользователя
                base_username = "testuser"
                base_slug = "testuser"
                
                # Проверка на уникальность username
                new_user = User(username=await self.generate_unique_username(session, base_username), 
                                firstname="Test", lastname="User", age=30, slug=await self.generate_unique_slug(session, base_slug))
                
                session.add(new_user)
                await session.commit()
                logger.info("Пользователь успешно создан.")

                # Создание задачи для пользователя
                new_task = Task(title="Test Task", content="This is a test task", priority=1, user_id=new_user.id)
                session.add(new_task)
                await session.commit()
                logger.info("Задача успешно создана.")

                # Запрос пользователя и его задач
                result = await session.execute(select(User).where(User.id == new_user.id))
                user = result.scalar_one_or_none()
                if user:
                    tasks = await session.execute(select(Task).where(Task.user_id == user.id))
                    tasks = tasks.scalars().all()
                    logger.info(f"Пользователь: {user.username}, Задачи: {len(tasks)}")
                else:
                    logger.error("Пользователь не найден.")
            except Exception as e:
                logger.error(f"Ошибка при тестировании операций с данными: {e}")
                raise

# Создаем экземпляр DatabaseManager
db_manager = DatabaseManager()

# Экспортируем engine для использования в других модулях
engine = db_manager.engine