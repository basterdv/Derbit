import asyncio
import logging
import time

import aiohttp
from celery import shared_task
from decouple import config

from app.database import SessionLocal, CurrencyPrice

logger = logging.getLogger(__name__)

TICKERS = ["btc_usd", "eth_usd"]

PROXY_URL = config("PROXY_URL")
PROXY_AUTH_LOGIN = config("PROXY_AUTH_LOGIN")
PROXY_AUTH_PASSWORD = config("PROXY_AUTH_PASSWORD")
PROXY_AUTH = aiohttp.BasicAuth(PROXY_AUTH_LOGIN, PROXY_AUTH_PASSWORD)


async def fetch_ticker(session, index_name):
    """Асинхронный запрос к Deribit через aiohttp."""
    url = f"https://deribit.com/api/v2/public/get_index_price?index_name={index_name}"
    try:
        async with session.get(url, proxy=PROXY_URL, proxy_auth=PROXY_AUTH, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            index_price = data.get("result", {}).get("index_price")
            ticker_short = index_name.split('_')[0]

            if index_price:
                return {
                    "ticker": ticker_short,
                    "price": float(index_price),
                    "timestamp": int(time.time())
                }
    except Exception as e:
        logger.error(f"Error fetching {index_name}: {e}")
        return None


async def run_fetch():
    """Параллельный сбор данных и сохранение в БД."""
    async with aiohttp.ClientSession() as session:
        # Собираем данные по всем тикерам параллельно
        tasks = [fetch_ticker(session, ticker) for ticker in TICKERS]
        results = await asyncio.gather(*tasks)

        db = SessionLocal()
        try:
            for res in results:
                if res:
                    new_entry = CurrencyPrice(**res)
                    db.add(new_entry)
            db.commit()
            print('Data saved successfully')
        except Exception as e:
            logger.error(f"DB Error: {e}")
            db.rollback()
        finally:
            db.close()


@shared_task(name="app.tasks.fetch_deribit_prices")
def fetch_deribit_prices():
    """Синхронная обертка Celery для асинхронного выполнения."""
    print('Working with aiohttp...')
    asyncio.run(run_fetch())
