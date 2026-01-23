import os
from sqlalchemy import create_engine, Column, Integer, Float, String, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Жестко прописанная строка без переменных
# jdbc:postgresql://localhost:5432/derbitdb
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/derbitdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CurrencyPrice(Base):
    __tablename__ = "currency_prices"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, index=True)
