from fastapi import FastAPI, Query, Depends
from sqlalchemy.orm import Session
import app.database as db
from app.database import  SessionLocal,engine ,Base ,CurrencyPrice
# import app.database as database

app = FastAPI()

# Создаст таблицы при запуске, если их нет
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/prices/all")
def get_all_prices(ticker: str = Query(...), db: Session = Depends(get_db)):
    return db.query(CurrencyPrice).filter(CurrencyPrice.ticker == ticker.lower()).all()

@app.get("/prices/latest")
def get_latest_price(ticker: str = Query(...), db: Session = Depends(get_db)):
    return db.query(CurrencyPrice).filter(CurrencyPrice.ticker == ticker.lower())\
             .order_by(CurrencyPrice.timestamp.desc()).first()

@app.get("/prices/filter")
def get_prices_by_date(
    ticker: str = Query(...),
    start_ts: int = Query(...),
    end_ts: int = Query(...),
    db: Session = Depends(get_db)
):
    return db.query(CurrencyPrice).filter(
        CurrencyPrice.ticker == ticker.lower(),
        CurrencyPrice.timestamp >= start_ts,
        CurrencyPrice.timestamp <= end_ts
    ).all()


@app.get("/")
async def root():
    return {"message": "Hello World"}


