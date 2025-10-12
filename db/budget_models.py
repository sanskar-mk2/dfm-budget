from sqlmodel import SQLModel, Field
from .core import engine


class Budget(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int
    amount: float
    year: int
    notes: str | None = None


# Create only your own tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)
