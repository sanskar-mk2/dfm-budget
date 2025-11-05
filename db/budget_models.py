from sqlalchemy import text
from sqlmodel import SQLModel, Field
from datetime import datetime
from .core import engine
from .dfm_reflect import DFMBase


class Budget(SQLModel, table=True):
    __tablename__ = "budget_2026"

    id: int | None = Field(default=None, primary_key=True)
    salesperson_id: int = Field(description="Salesperson ID")
    salesperson_name: str = Field(max_length=255, description="Salesperson Name")
    brand: str | None = Field(default=None, max_length=255, description="Brand")
    flag: str | None = Field(default=None, max_length=255, description="Flag")
    customer_name: str | None = Field(
        default=None, max_length=255, description="Customer Name"
    )
    customer_class: str = Field(max_length=255, description="Customer Class")
    quarter_1_sales: float = Field(default=0.0, description="Quarter 1 Sales")
    quarter_2_sales: float = Field(default=0.0, description="Quarter 2 Sales")
    quarter_3_sales: float = Field(default=0.0, description="Quarter 3 Sales")
    quarter_4_sales: float = Field(default=0.0, description="Quarter 4 Sales")
    is_custom: bool = Field(default=False, description="Is Custom Budget")


class DivisionRatioOverride(SQLModel, table=True):
    __tablename__ = "division_ratio_overrides"

    id: int | None = Field(default=None, primary_key=True)
    salesperson_id: int = Field(description="Salesperson ID")
    salesperson_name: str = Field(max_length=255, description="Salesperson Name")
    customer_class: str = Field(max_length=50, description="Customer Class")
    group_key: str = Field(max_length=255, description="Group Key")
    item_division: int = Field(description="Item Division Number")
    custom_ratio: float = Field(description="Custom Division Ratio")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Created At"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Updated At"
    )

    class Config:
        # Composite unique constraint
        indexes = [
            {
                "fields": [
                    "salesperson_id",
                    "customer_class",
                    "group_key",
                    "item_division",
                ],
                "unique": True,
            }
        ]


class GrossProfitOverride(SQLModel, table=True):
    __tablename__ = "gp_ratio_overrides"

    id: int | None = Field(default=None, primary_key=True)
    salesperson_id: int
    salesperson_name: str = Field(max_length=255, description="Salesperson Name")
    customer_class: str = Field(max_length=50, description="Customer Class")
    group_key: str = Field(max_length=255, description="Group Key")
    custom_q1_gp_percent: float | None = Field(default=None, description="Custom Q1 GP% (0.0–1.0 range)")
    custom_q2_gp_percent: float | None = Field(default=None, description="Custom Q2 GP% (0.0–1.0 range)")
    custom_q3_gp_percent: float | None = Field(default=None, description="Custom Q3 GP% (0.0–1.0 range)")
    custom_q4_gp_percent: float | None = Field(default=None, description="Custom Q4 GP% (0.0–1.0 range)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        indexes = [
            {
                "fields": ["salesperson_id", "customer_class", "group_key"],
                "unique": True,
            }
        ]


# Create only your own tables
def init_db():
    create_budget_clone_tables()
    SQLModel.metadata.create_all(bind=engine)
    DFMBase.prepare(autoload_with=engine)


def create_budget_clone_tables():
    """Clone structures for budget tables without touching the source tables."""
    statements = (
        "CREATE TABLE IF NOT EXISTS sales_budget_2026 LIKE sales",
        "CREATE TABLE IF NOT EXISTS orders_budget_2026 LIKE open_orders",
    )
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
