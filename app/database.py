from decouple import config
from sqlalchemy import create_engine, Column, Integer, Float, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_USER=config("POSTGRES_USER")
POSTGRES_PASSWORD=config("POSTGRES_PASSWORD")
POSTGRES_DB=config("POSTGRES_DB")
POSTGRES_HOST=config("POSTGRES_HOST")
POSTGRES_PORT=config("POSTGRES_PORT")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CurrencyPrice(Base):
    __tablename__ = "currency_prices"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, index=True)
