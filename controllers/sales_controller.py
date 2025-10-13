from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session
from servies.sales_service import SalesService
from servies.admin_service import AdminService
from typing import Dict, Any

router = APIRouter(
    tags=["sales"],
)


@router.get("/sales")
async def get_sales_data(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get sales data based on user's salesperson role
    """
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize sales service
        sales_service = SalesService(db)

        # Get sales data based on user role
        sales_data = sales_service.get_sales_data(username)
        summary = sales_service.get_sales_summary(username)

        # Get user's salesperson info for context
        user_salesperson = sales_service._get_user_salesperson(username)
        user_role = user_salesperson.role if user_salesperson else "Unknown"

        return {
            "success": True,
            "data": sales_data,
            "summary": summary,
            "user_info": {
                "username": username,
                "role": user_role,
                "is_hospitality": (user_role or "").startswith("Hospitality"),
                "salesperson_id": (
                    user_salesperson.salesman_no if user_salesperson else None
                ),
            },
            "total_records": len(sales_data),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching sales data: {str(e)}"
        )


@router.get("/sales/summary")
async def get_sales_summary(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get sales summary only
    """
    try:
        username = request.state.user["username"]
        sales_service = SalesService(db)
        summary = sales_service.get_sales_summary(username)

        return {"success": True, "summary": summary}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching sales summary: {str(e)}"
        )


@router.get("/sales/{salesperson_id}")
async def get_salesperson_sales_data(
    salesperson_id: int, request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get sales data for a specific salesperson (admin only)
    """
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

        # Initialize sales service
        sales_service = SalesService(db)

        # Get sales data for the specific salesperson
        # We need to get the salesperson's role first to determine the logic
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

        # Get sales data using the same logic as regular sales service
        role = salesperson.role or ""
        is_hospitality = role.startswith("Hospitality")

        if is_hospitality:
            sales_data = sales_service._get_hospitality_sales_data(salesperson_id)
        else:
            sales_data = sales_service._get_non_hospitality_sales_data(salesperson_id)

        summary = sales_service.get_sales_summary_for_salesperson(sales_data)

        return {
            "success": True,
            "data": sales_data,
            "summary": summary,
            "salesperson_info": {
                "salesperson_id": salesperson_id,
                "salesperson_name": salesperson.salesman_name,
                "role": role,
                "is_hospitality": is_hospitality,
            },
            "total_records": len(sales_data),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching salesperson sales data: {str(e)}"
        )
