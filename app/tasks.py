import requests
import time
import logging
from app.celery_app import app
from app.database import SessionLocal, CurrencyPrice

logger = logging.getLogger(__name__)

# Список тикеров для мониторинга
TICKERS = ["btc_usd", "eth_usd"]

proxies = {
    'http': 'http://7AFJmS:uG27aQ@163.198.111.111:8000',
    'https': 'http://7AFJmS:uG27aQ@163.198.111.111:8000',
}



@app.task(name="fetch_deribit_prices")
def fetch_deribit_prices():
    print('gggggggggggggggggggggggggg')
    """Задача для получения цен и сохранения в БД."""
    db = SessionLocal()

    # try:
    for index_name in TICKERS:
            # API Deribit: https://docs.deribit.com
            url = f"https://deribit.com/api/v2/public/get_index_price?index_name={index_name}"
            response = requests.get(url, proxies=proxies, timeout=10)
            response.raise_for_status()

            data = response.json()
            # Извлекаем цену из ответа
            index_price = data.get("result", {}).get("index_price")
            # Убираем '_usd' для сохранения чистого тикера (btc, eth)
            ticker_short = index_name.split('_')[0]

            if index_price:
                new_entry = CurrencyPrice(
                    ticker=ticker_short,
                    price=float(index_price),
                    timestamp=int(time.time())  # UNIX timestamp
                )
                db.add(new_entry)
                logger.info(f"Saved: {ticker_short} - {index_price}")

    db.commit()
    # except Exception as e:
    #     logger.error(f"Error fetching prices: {e}")
    #     db.rollback()
    # finally:
    #     db.close()
