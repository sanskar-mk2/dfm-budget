from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session
from typing import List
from pydantic import BaseModel
from db.core import get_readonly_session, get_session
from services.admin_service import AdminService
from services.gross_profit_service import GrossProfitService

router = APIRouter(tags=["gross-profit"])


class GpOverride(BaseModel):
    salesperson_id: int
    salesperson_name: str
    customer_class: str
    group_key: str
    custom_gp_percent: float


class SaveGpOverrides(BaseModel):
    overrides: List[GpOverride]


@router.get("/gross-profit")
async def get_gp(request: Request, db: Session = Depends(get_readonly_session)):
    username = request.state.user["username"]
    admin = AdminService(db)
    if not admin.is_admin(username):
        raise HTTPException(status_code=403, detail="Access denied")
    data = GrossProfitService(db).get_gross_profit_allocations()
    return {"success": True, "data": data, "count": len(data)}


@router.post("/gross-profit/save-overrides")
async def save_gp_overrides(
    request: Request, payload: SaveGpOverrides, db: Session = Depends(get_session)
):
    username = request.state.user["username"]
    admin = AdminService(db)
    if not admin.is_admin(username):
        raise HTTPException(status_code=403, detail="Access denied")
    result = GrossProfitService(db).save_gp_overrides(
        [o.dict() for o in payload.overrides]
    )
    return {"success": True, "result": result}


@router.delete("/gross-profit/reset/{salesperson_id}/{customer_class}/{group_key}")
async def reset_gp_override(
    salesperson_id: int,
    customer_class: str,
    group_key: str,
    request: Request,
    db: Session = Depends(get_session),
):
    username = request.state.user["username"]
    admin = AdminService(db)
    if not admin.is_admin(username):
        raise HTTPException(status_code=403, detail="Access denied")
    deleted = GrossProfitService(db).delete_gp_override(
        salesperson_id, customer_class, group_key
    )
    return {"success": True, "deleted": deleted}
