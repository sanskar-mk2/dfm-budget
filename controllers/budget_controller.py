from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session, get_session
from services.budget_service import BudgetService
from services.sales_service import SalesService
from services.admin_service import AdminService
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
    customer_name: str | None = None
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
    """Create a new budget entry, ensuring no duplicate (salesperson_id, salesperson_name, brand, flag, customer_name, customer_class)"""
    try:
        budget_service = BudgetService(db)
        # Check for duplicate
        existing_budgets = budget_service.get_budgets_by_salesperson(
            budget_data.salesperson_id
        )
        for b in existing_budgets:
            if (
                b["salesperson_id"] == budget_data.salesperson_id
                and b["salesperson_name"] == budget_data.salesperson_name
                and b["brand"] == budget_data.brand
                and b["flag"] == budget_data.flag
                and b["customer_name"] == budget_data.customer_name
                and b["customer_class"] == budget_data.customer_class
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Identical budget entry already exists for this salesperson.",
                )

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

    except HTTPException:
        raise
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
    """Returns customer_classes, customer_names, brands, and flags for autosuggest"""
    try:
        # Get autosuggest data
        budget_service = BudgetService(db)
        customer_classes = budget_service.get_unique_customer_classes()
        customer_names = budget_service.get_unique_customer_names()
        brands = budget_service.get_unique_brands()
        flags = budget_service.get_unique_flags()

        return {
            "success": True,
            "data": {
                "customer_classes": customer_classes,
                "customer_names": customer_names,
                "brands": brands,
                "flags": flags,
            },
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


@router.get("/budget/{salesperson_id}")
async def get_salesperson_budgets(
    salesperson_id: int, request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """Get all budgets for a specific salesperson (admin only)"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service to check admin privileges
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Get salesperson info
        from db.dfm_reflect import Salesperson
        from sqlmodel import select

        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == salesperson_id)
        ).first()

        if not salesperson:
            raise HTTPException(
                status_code=404,
                detail=f"Salesperson with ID {salesperson_id} not found",
            )

        # Get budgets
        budget_service = BudgetService(db)
        budgets = budget_service.get_budgets_by_salesperson(salesperson_id)
        summary = budget_service.get_budget_summary(salesperson_id)

        return {
            "success": True,
            "data": budgets,
            "summary": summary,
            "salesperson_info": {
                "salesperson_id": salesperson_id,
                "salesperson_name": salesperson.salesman_name,
                "role": salesperson.role or "Unknown",
            },
            "total_records": len(budgets),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching salesperson budget data: {str(e)}"
        )


@router.post("/budget/{salesperson_id}")
async def create_salesperson_budget(
    salesperson_id: int,
    budget_data: BudgetCreate,
    request: Request,
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Create a new budget entry for a specific salesperson (admin only), preventing duplicates"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service to check admin privileges
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Verify salesperson exists
        from db.dfm_reflect import Salesperson
        from sqlmodel import select

        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == salesperson_id)
        ).first()

        if not salesperson:
            raise HTTPException(
                status_code=404,
                detail=f"Salesperson with ID {salesperson_id} not found",
            )

        # Override the salesperson_id and name in the budget data
        budget_data_dict = budget_data.dict()
        budget_data_dict["salesperson_id"] = salesperson_id
        budget_data_dict["salesperson_name"] = salesperson.salesman_name

        budget_service = BudgetService(db)
        # Duplicate prevention logic (same as POST /budget)
        existing_budgets = budget_service.get_budgets_by_salesperson(salesperson_id)
        for b in existing_budgets:
            if (
                b["salesperson_id"] == salesperson_id
                and b["salesperson_name"] == salesperson.salesman_name
                and b["brand"] == budget_data_dict.get("brand")
                and b["flag"] == budget_data_dict.get("flag")
                and b["customer_name"] == budget_data_dict.get("customer_name")
                and b["customer_class"] == budget_data_dict.get("customer_class")
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Identical budget entry already exists for this salesperson.",
                )

        budget = budget_service.create_budget(budget_data_dict)

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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating salesperson budget: {str(e)}"
        )


@router.put("/budget/{salesperson_id}/{budget_id}")
async def update_salesperson_budget(
    salesperson_id: int,
    budget_id: int,
    budget_data: BudgetUpdate,
    request: Request,
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Update an existing budget entry for a specific salesperson (admin only)"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service to check admin privileges
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Verify salesperson exists
        from db.dfm_reflect import Salesperson
        from sqlmodel import select

        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == salesperson_id)
        ).first()

        if not salesperson:
            raise HTTPException(
                status_code=404,
                detail=f"Salesperson with ID {salesperson_id} not found",
            )

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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating salesperson budget: {str(e)}"
        )


@router.delete("/budget/{salesperson_id}/{budget_id}")
async def delete_salesperson_budget(
    salesperson_id: int,
    budget_id: int,
    request: Request,
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Delete a budget entry for a specific salesperson (admin only)"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service to check admin privileges
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Verify salesperson exists
        from db.dfm_reflect import Salesperson
        from sqlmodel import select

        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == salesperson_id)
        ).first()

        if not salesperson:
            raise HTTPException(
                status_code=404,
                detail=f"Salesperson with ID {salesperson_id} not found",
            )

        budget_service = BudgetService(db)
        success = budget_service.delete_budget(budget_id)

        if not success:
            raise HTTPException(status_code=404, detail="Budget not found")

        return {"success": True, "message": "Budget deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting salesperson budget: {str(e)}"
        )


@router.post("/budget/{salesperson_id}/generate-from-sales")
async def generate_salesperson_budget_from_sales(
    salesperson_id: int, request: Request, db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Generate budget entries from sales data for a specific salesperson (admin only)"""
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service to check admin privileges
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Verify salesperson exists and get their info
        from db.dfm_reflect import Salesperson
        from sqlmodel import select

        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == salesperson_id)
        ).first()

        if not salesperson:
            raise HTTPException(
                status_code=404,
                detail=f"Salesperson with ID {salesperson_id} not found",
            )

        # Get sales data for this salesperson
        sales_service = SalesService(db)
        role = salesperson.role or ""
        is_hospitality = role.startswith("Hospitality")

        if is_hospitality:
            sales_data = sales_service._get_hospitality_sales_data(salesperson_id)
        else:
            sales_data = sales_service._get_non_hospitality_sales_data(salesperson_id)

        # Generate budgets from sales data
        budget_service = BudgetService(db)
        budgets = budget_service.generate_budget_from_sales(
            salesperson_id, salesperson.salesman_name, sales_data
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating salesperson budget from sales: {str(e)}",
        )
