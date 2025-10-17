from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session, get_session
from services.admin_service import AdminService
from services.division_service import DivisionService
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter(
    tags=["division"],
)


class RatioOverrideRequest(BaseModel):
    salesperson_id: int
    salesperson_name: str
    customer_class: str
    group_key: str
    item_division: int
    custom_ratio: float


class SaveRatiosRequest(BaseModel):
    overrides: List[RatioOverrideRequest]


@router.get("/division/allocations")
async def get_division_allocations(
    request: Request, db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get division allocations based on historical sales ratios and budget data
    Only accessible by admin users
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

        # Initialize division service and get data
        division_service = DivisionService(db)
        division_data = division_service.get_division_allocations()

        return {
            "success": True,
            "data": division_data,
            "total_records": len(division_data),
            "user_info": {"username": username, "is_admin": True},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching division allocations: {str(e)}"
        )


@router.post("/division/save-ratios")
async def save_division_ratios(
    request: Request, 
    save_request: SaveRatiosRequest,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Save custom division ratio overrides
    Only accessible by admin users
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

        # Initialize division service and save overrides
        division_service = DivisionService(db)
        
        # Convert Pydantic models to dictionaries
        overrides_data = [override.dict() for override in save_request.overrides]
        
        result = division_service.save_ratio_overrides(overrides_data)

        return {
            "success": True,
            "message": f"Successfully saved {result['saved_count']} new overrides and updated {result['updated_count']} existing overrides",
            "result": result,
            "user_info": {"username": username, "is_admin": True},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving division ratios: {str(e)}"
        )


@router.get("/division/allocations/{salesperson_id}/{customer_class}/{group_key}")
async def get_single_division_allocation(
    salesperson_id: int,
    customer_class: str,
    group_key: str,
    request: Request,
    db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Get allocations for a single group only
    Only accessible by admin users
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

        # Initialize division service and get data for single group
        division_service = DivisionService(db)
        data = division_service.get_division_allocations_for_group(
            salesperson_id, customer_class, group_key
        )

        return {
            "success": True,
            "data": data,
            "count": len(data),
            "user_info": {"username": username, "is_admin": True},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching single group allocations: {str(e)}"
        )


@router.delete("/division/reset-group/{salesperson_id}/{customer_class}/{group_key}")
async def reset_group_overrides(
    salesperson_id: int,
    customer_class: str, 
    group_key: str,
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Reset custom division ratio overrides for a specific group
    Only accessible by admin users
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

        # Initialize division service and delete overrides
        division_service = DivisionService(db)
        deleted_count = division_service.delete_group_overrides(salesperson_id, customer_class, group_key)

        return {
            "success": True,
            "message": f"Successfully reset {deleted_count} custom overrides for group",
            "deleted_count": deleted_count,
            "user_info": {"username": username, "is_admin": True},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error resetting group overrides: {str(e)}"
        )
