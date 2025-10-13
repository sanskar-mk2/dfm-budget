from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session, get_session
from servies.budget_service import BudgetService
from servies.sales_service import SalesService
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter(
    tags=["budget"],
)


class BudgetCreate(BaseModel):
    salesperson_id: int
    salesperson_name: str
    brand: str | None = None
    flag: str | None = None
    customer_name: str
    customer_class: str
    quarter_1_sales: float = 0.0
    quarter_2_sales: float = 0.0
    quarter_3_sales: float = 0.0
    quarter_4_sales: float = 0.0
    is_custom: bool = False


class BudgetUpdate(BaseModel):
    brand: str | None = None
    flag: str | None = None
    customer_name: str | None = None
    customer_class: str | None = None
    quarter_1_sales: float | None = None
    quarter_2_sales: float | None = None
    quarter_3_sales: float | None = None
    quarter_4_sales: float | None = None
    is_custom: bool | None = None


@router.get("/budget")
async def get_budgets(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """Get all budgets for the current salesperson"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Get salesperson info
        sales_service = SalesService(db)
        user_salesperson = sales_service._get_user_salesperson(username)

        if not user_salesperson:
            raise HTTPException(status_code=404, detail="Salesperson not found")

        # Get budgets
        budget_service = BudgetService(db)
        budgets = budget_service.get_budgets_by_salesperson(
            user_salesperson.salesman_no
        )
        summary = budget_service.get_budget_summary(user_salesperson.salesman_no)

        return {
            "success": True,
            "data": budgets,
            "summary": summary,
            "user_info": {
                "username": username,
                "salesperson_id": user_salesperson.salesman_no,
                "salesperson_name": user_salesperson.salesman_name,
            },
            "total_records": len(budgets),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching budget data: {str(e)}"
        )


@router.post("/budget")
async def create_budget(
    budget_data: BudgetCreate, request: Request, db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new budget entry"""
    try:
        budget_service = BudgetService(db)
        budget = budget_service.create_budget(budget_data.dict())

        return {
            "success": True,
            "data": {
                "id": budget.id,
                "salesperson_id": budget.salesperson_id,
                "salesperson_name": budget.salesperson_name,
                "brand": budget.brand,
                "flag": budget.flag,
                "customer_name": budget.customer_name,
                "customer_class": budget.customer_class,
                "quarter_1_sales": budget.quarter_1_sales,
                "quarter_2_sales": budget.quarter_2_sales,
                "quarter_3_sales": budget.quarter_3_sales,
                "quarter_4_sales": budget.quarter_4_sales,
                "is_custom": budget.is_custom,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating budget: {str(e)}")


@router.put("/budget/{budget_id}")
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    request: Request,
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Update an existing budget entry"""
    try:
        budget_service = BudgetService(db)
        budget = budget_service.update_budget(
            budget_id, budget_data.dict(exclude_unset=True)
        )

        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        return {
            "success": True,
            "data": {
                "id": budget.id,
                "salesperson_id": budget.salesperson_id,
                "salesperson_name": budget.salesperson_name,
                "brand": budget.brand,
                "flag": budget.flag,
                "customer_name": budget.customer_name,
                "customer_class": budget.customer_class,
                "quarter_1_sales": budget.quarter_1_sales,
                "quarter_2_sales": budget.quarter_2_sales,
                "quarter_3_sales": budget.quarter_3_sales,
                "quarter_4_sales": budget.quarter_4_sales,
                "is_custom": budget.is_custom,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating budget: {str(e)}")


@router.delete("/budget/{budget_id}")
async def delete_budget(
    budget_id: int, request: Request, db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Delete a budget entry"""
    try:
        budget_service = BudgetService(db)
        success = budget_service.delete_budget(budget_id)

        if not success:
            raise HTTPException(status_code=404, detail="Budget not found")

        return {"success": True, "message": "Budget deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting budget: {str(e)}")


@router.get("/budget/autosuggest")
async def get_autosuggest_data(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """Returns customer_classes and brands for autosuggest"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Get salesperson info
        sales_service = SalesService(db)
        user_salesperson = sales_service._get_user_salesperson(username)

        if not user_salesperson:
            raise HTTPException(status_code=404, detail="Salesperson not found")

        # Get autosuggest data
        budget_service = BudgetService(db)
        customer_classes = budget_service.get_unique_customer_classes(user_salesperson.salesman_no)
        brands = budget_service.get_unique_brands(user_salesperson.salesman_no)

        return {
            "success": True,
            "data": {
                "customer_classes": customer_classes,
                "brands": brands
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching autosuggest data: {str(e)}"
        )


@router.post("/budget/generate-from-sales")
async def generate_budget_from_sales(
    request: Request, db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Generate budget entries from current sales data"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Get sales data
        sales_service = SalesService(db)
        sales_data = sales_service.get_sales_data(username)
        user_salesperson = sales_service._get_user_salesperson(username)

        if not user_salesperson:
            raise HTTPException(status_code=404, detail="Salesperson not found")

        # Generate budgets from sales data
        budget_service = BudgetService(db)
        budgets = budget_service.generate_budget_from_sales(
            user_salesperson.salesman_no, user_salesperson.salesman_name, sales_data
        )

        # Save budgets to database
        created_budgets = []
        for budget in budgets:
            db.add(budget)
            created_budgets.append(budget)

        db.commit()

        # Refresh to get IDs
        for budget in created_budgets:
            db.refresh(budget)

        return {
            "success": True,
            "message": f"Generated {len(created_budgets)} budget entries from sales data",
            "data": [
                {
                    "id": budget.id,
                    "salesperson_id": budget.salesperson_id,
                    "salesperson_name": budget.salesperson_name,
                    "brand": budget.brand,
                    "flag": budget.flag,
                    "customer_name": budget.customer_name,
                    "customer_class": budget.customer_class,
                    "quarter_1_sales": budget.quarter_1_sales,
                    "quarter_2_sales": budget.quarter_2_sales,
                    "quarter_3_sales": budget.quarter_3_sales,
                    "quarter_4_sales": budget.quarter_4_sales,
                    "is_custom": budget.is_custom,
                }
                for budget in created_budgets
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating budget from sales: {str(e)}"
        )
