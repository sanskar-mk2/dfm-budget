from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session
from servies.sales_service import SalesService
from typing import Dict, Any

router = APIRouter(
    tags=["sales"],
)


@router.get("/sales")
async def get_sales_data(
    request: Request,
    db: Session = Depends(get_readonly_session)
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
                "salesperson_id": user_salesperson.salesman_no if user_salesperson else None
            },
            "total_records": len(sales_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching sales data: {str(e)}"
        )


@router.get("/sales/summary")
async def get_sales_summary(
    request: Request,
    db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get sales summary only
    """
    try:
        username = request.state.user["username"]
        sales_service = SalesService(db)
        summary = sales_service.get_sales_summary(username)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching sales summary: {str(e)}"
        )


