import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./buildathon.db")
POOL_RECYCLE_SECONDS = int(os.getenv("DATABASE_POOL_RECYCLE_SECONDS", "1800"))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=POOL_RECYCLE_SECONDS,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_database_runtime_info() -> dict[str, str]:
    url = make_url(DATABASE_URL)
    return {
        "backend": url.get_backend_name(),
        "driver": url.get_driver_name(),
        "database": url.database or "",
    }


def get_database_health() -> dict[str, str]:
    details = get_database_runtime_info()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", **details}
    except Exception as exc:
        return {"status": "error", "detail": exc.__class__.__name__, **details}


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
