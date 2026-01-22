from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL (temporary SQLite, works out of the box)
SQLALCHEMY_DATABASE_URL = "sqlite:///./infra.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 👇 THIS WAS MISSING
Base = declarative_base()
