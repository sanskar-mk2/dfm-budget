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
        print(f"Get allocations - Username: {username}")

        # Initialize admin service
        admin_service = AdminService(db)

        # Check if user is admin
        is_admin_result = admin_service.is_admin(username)
        print(f"Get allocations - Is admin check result: {is_admin_result}")
        
        if not is_admin_result:
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
        print(f"Save ratios - Username: {username}")

        # Initialize admin service
        admin_service = AdminService(db)

        # Check if user is admin
        is_admin_result = admin_service.is_admin(username)
        print(f"Save ratios - Is admin check result: {is_admin_result}")
        
        if not is_admin_result:
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
