# app/controllers/gross_profit_controller.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from db.core import get_readonly_session
from services.admin_service import AdminService
from services.gross_profit_service import GrossProfitService

router = APIRouter(tags=["gross-profit"])


@router.get("/gross-profit")
async def get_gross_profit(
    request: Request, db: Session = Depends(get_readonly_session)
):
    try:
        username = request.state.user["username"]
        admin_service = AdminService(db)
        if not admin_service.is_admin(username):
            raise HTTPException(status_code=403, detail="Access denied")

        service = GrossProfitService(db)
        data = service.get_gross_profit_allocations()
        return {"success": True, "data": data, "total_records": len(data)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching GP data: {e}")
