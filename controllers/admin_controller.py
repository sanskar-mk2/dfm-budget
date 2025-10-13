from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session
from servies.admin_service import AdminService
from typing import Dict, Any

router = APIRouter(
    tags=["admin"],
)


@router.get("/admin/summary")
async def get_admin_summary(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get admin summary of all salespeople with their sales and budget data
    Only accessible by admin users (salesman_id = 0 or null)
    """
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service
        admin_service = AdminService(db)

        # Check if user is admin
        if not admin_service.is_admin(username):
            raise HTTPException(
                status_code=403, detail="Access denied. Admin privileges required."
            )

        # Get admin summary data
        summary_data = admin_service.get_admin_summary()

        return {
            "success": True,
            "data": summary_data,
            "total_salespeople": len(summary_data),
            "user_info": {"username": username, "is_admin": True},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching admin summary: {str(e)}"
        )


@router.get("/salesperson/{salesperson_id}/info")
async def get_salesperson_info(
    salesperson_id: int, request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get salesperson information (admin only)
    """
    try:
        # Get username from request state (set by auth middleware)
        username = request.state.user["username"]

        # Initialize admin service
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

        return {
            "success": True,
            "data": {
                "salesperson_id": salesperson.salesman_no,
                "salesperson_name": salesperson.salesman_name,
                "role": salesperson.role or "Unknown",
                "is_hospitality": (salesperson.role or "").startswith("Hospitality"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching salesperson info: {str(e)}"
        )
