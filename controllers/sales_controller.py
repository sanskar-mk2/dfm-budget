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


@router.get("/sales/raw")
async def get_raw_sales_data(
    request: Request,
    db: Session = Depends(get_readonly_session),
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get raw sales data for debugging (limited)
    """
    try:
        from db.dfm_reflect import Sales
        from sqlmodel import text
        
        # Get raw sales data
        result = db.exec(text(f"SELECT * FROM sales LIMIT {limit}"))
        sales_data = [dict(row._mapping) for row in result]
        
        # Get sample of open_orders too
        result_orders = db.exec(text(f"SELECT * FROM open_orders LIMIT {limit}"))
        orders_data = [dict(row._mapping) for row in result_orders]
        
        # Get user info for debugging
        username = request.state.user["username"]
        sales_service = SalesService(db)
        user_salesperson = sales_service._get_user_salesperson(username)
        
        return {
            "success": True,
            "sales_data": sales_data,
            "orders_data": orders_data,
            "user_info": {
                "username": username,
                "salesperson": user_salesperson.__dict__ if user_salesperson else None
            },
            "total_sales_records": len(sales_data),
            "total_orders_records": len(orders_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching raw sales data: {str(e)}"
        )


@router.get("/sales/debug")
async def debug_sales_data(
    request: Request,
    db: Session = Depends(get_readonly_session)
) -> Dict[str, Any]:
    """
    Debug endpoint to check data structure and queries
    """
    try:
        from sqlmodel import text
        
        # Get user's salesperson info
        username = request.state.user["username"]
        sales_service = SalesService(db)
        user_salesperson = sales_service._get_user_salesperson(username)
        salesman_no = user_salesperson.salesman_no if user_salesperson else None
        
        # Check what's in sales table for this salesperson
        sales_sample = db.exec(text(f"SELECT flag, brand, customer_name, period, ext_sales, zero_perc_sales FROM sales WHERE salesperson = {salesman_no} LIMIT 5"))
        sales_sample_data = [dict(row._mapping) for row in sales_sample]
        
        # Check period ranges for this salesperson
        period_info = db.exec(text(f"SELECT MIN(period) as min_period, MAX(period) as max_period, COUNT(*) as total_records, COUNT(DISTINCT period) as unique_periods FROM sales WHERE salesperson = {salesman_no}"))
        period_data = dict(period_info.first()._mapping)
        
        # Check what periods exist
        periods = db.exec(text(f"SELECT DISTINCT period FROM sales WHERE salesperson = {salesman_no} ORDER BY period"))
        period_list = [row.period for row in periods]
        
        # Check what's in open_orders table
        orders_sample = db.exec(text("SELECT customer_name, ext_sales, requested_ship_date FROM open_orders LIMIT 5"))
        orders_sample_data = [dict(row._mapping) for row in orders_sample]
        
        # Check date ranges in open_orders
        date_info = db.exec(text("SELECT MIN(requested_ship_date) as min_date, MAX(requested_ship_date) as max_date, COUNT(*) as total_records FROM open_orders"))
        date_data = dict(date_info.first()._mapping)
        
        return {
            "success": True,
            "salesman_no": salesman_no,
            "sales_sample": sales_sample_data,
            "orders_sample": orders_sample_data,
            "period_info": period_data,
            "period_list": period_list,
            "date_info": date_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error in debug: {str(e)}"
        )
