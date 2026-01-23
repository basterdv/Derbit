import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.database import Base, CurrencyPrice

# Настройка тестовой БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределение зависимости get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Фикстура для подготовки данных
@pytest.fixture
def db_session():
    # Создаем таблицы перед тестом
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Наполняем тестовыми данными
    db.add_all([
        CurrencyPrice(ticker="btc", price=89113.07, timestamp=1769170370),
        CurrencyPrice(ticker="btc", price=89110.54, timestamp=1769170372),
        CurrencyPrice(ticker="eth", price=89075.38, timestamp=1769170432),
    ])
    db.commit()

    yield db

    # Очищаем базу после каждого теста
    db.close()
    Base.metadata.drop_all(bind=engine)


# ---  ТЕСТЫ ---

def test_get_all_prices(db_session):
    response = client.get("/prices/all", params={"ticker": "BTC"})  # Проверка регистра
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["ticker"] == "btc" for item in data)


def test_get_latest_price(db_session):
    response = client.get("/prices/latest", params={"ticker": "btc"})
    assert response.status_code == 200
    data = response.json()
    # Проверяем, что вернулась запись с самым большим timestamp (1769170432)
    assert data["timestamp"] == 1769170372
    assert data["price"] == 89110.54


def test_get_prices_by_date_filter(db_session):
    params = {
        "ticker": "btc",
        "start_ts": 1769170371,
        "end_ts": 1769170372
    }
    response = client.get("/prices/filter", params=params)
    assert response.status_code == 200
    data = response.json()
    # Должна вернуться только одна запись (timestamp 1769170372)
    assert len(data) == 1
    assert data[0]["timestamp"] == 1769170372


def test_root_redirect():
    # Для этого теста БД не нужна, так как это простой редирект
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
