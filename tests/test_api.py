import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base, CurrencyPrice

# Создаем тестовую БД в памяти (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client():
    # Создаем таблицы для тестов
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Подменяем зависимость БД в приложении
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    # Очищаем БД после тестов
    Base.metadata.drop_all(bind=engine)


def test_read_all_prices(client):
    # Добавляем тестовые данные
    db = TestingSessionLocal()
    db.add(CurrencyPrice(ticker="btc_usd", price=50000.0, timestamp=1678886400))
    db.commit()
    db.close()

    response = client.get("/prices/all?ticker=btc_usd")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['price'] == 50000.0
