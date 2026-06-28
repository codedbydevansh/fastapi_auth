# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# # For SQLite, we need check_same_thread: False
# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Robust URL handling for Pylance
raw_url = os.getenv("DATABASE_URL", "sqlite:///./local.db")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL: str = raw_url # Force string type

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()