from sqlmodel import SQLModel, Field
from datetime import datetime
from .core import engine


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
    custom_gp_percent: float  # 0.0–1.0 range (e.g., 0.52)
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
    SQLModel.metadata.create_all(bind=engine)
