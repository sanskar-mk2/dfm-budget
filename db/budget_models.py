from sqlmodel import SQLModel, Field
from .core import engine


class Budget(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    salesperson_id: int = Field(description="Salesperson ID")
    salesperson_name: str = Field(description="Salesperson Name")
    brand: str | None = Field(default=None, description="Brand")
    flag: str | None = Field(default=None, description="Flag")
    customer_name: str = Field(description="Customer Name")
    customer_class: str = Field(description="Customer Class")
    quarter_1_sales: float = Field(default=0.0, description="Quarter 1 Sales")
    quarter_2_sales: float = Field(default=0.0, description="Quarter 2 Sales")
    quarter_3_sales: float = Field(default=0.0, description="Quarter 3 Sales")
    quarter_4_sales: float = Field(default=0.0, description="Quarter 4 Sales")
    is_custom: bool = Field(default=False, description="Is Custom Budget")


# Create only your own tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)
