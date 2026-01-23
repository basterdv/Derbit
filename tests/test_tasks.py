from unittest.mock import patch, MagicMock

import pytest
from aioresponses import aioresponses
from decouple import config

from app.tasks import fetch_ticker, run_fetch, TICKERS


@pytest.mark.asyncio
async def test_fetch_ticker_success():
    """Тест успешного получения данных от API Deribit."""
    index_name = "btc_usd"
    mock_url = f"https://deribit.com/api/v2/public/get_index_price?index_name={index_name}"
    mock_response = {"result": {"index_price": 50000.5}}

    with aioresponses() as m:
        m.get(mock_url, payload=mock_response)

        import aiohttp
        async with aiohttp.ClientSession() as session:
            result = await fetch_ticker(session, index_name)

    assert result is not None
    assert result["ticker"] == "btc"
    assert result["price"] == 50000.5
    assert isinstance(result["timestamp"], int)

@pytest.mark.asyncio
async def test_fetch_ticker_error():
    """Тест обработки ошибки API (например, 500 или таймаут)."""
    index_name = "eth_usd"
    mock_url = f"https://deribit.com/api/v2/public/get_index_price?index_name={index_name}"

    with aioresponses() as m:
        m.get(mock_url, status=500)

        import aiohttp
        async with aiohttp.ClientSession() as session:
            result = await fetch_ticker(session, index_name)

    assert result is None

@pytest.mark.asyncio
@patch("app.tasks.SessionLocal")
async def test_run_fetch_db_integration(mock_session_local):
    """Тест всей цепочки: получение данных и вызов методов БД."""
    # Настройка мока БД
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    # Данные для имитации ответов API
    mock_responses = {
        "btc_usd": 60000.0,
        "eth_usd": 3000.0
    }

    with aioresponses() as m:
        for ticker, price in mock_responses.items():
            url = f"https://deribit.com/api/v2/public/get_index_price?index_name={ticker}"
            m.get(url, payload={"result": {"index_price": price}})

        await run_fetch()

    # Проверяем, что в базу было добавлено столько записей, сколько тикеров в TICKERS
    assert mock_db.add.call_count == len(TICKERS)
    assert mock_db.commit.called is True
    mock_db.close.assert_called_once()




