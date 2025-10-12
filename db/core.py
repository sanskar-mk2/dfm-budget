from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()


engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)


# ----- Sessions -----
def get_session():
    """Normal writable session (for Budget)."""
    with Session(engine) as session:
        yield session


def get_readonly_session():
    """Read-only session for reflected DFM tables."""
    with Session(engine) as session:
        yield session
        session.rollback()  # ensure nothing gets committed accidentally
