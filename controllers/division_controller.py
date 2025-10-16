from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session, text
from db.core import get_readonly_session
from services.admin_service import AdminService
from typing import Dict, Any, List

router = APIRouter(
    tags=["division"],
)


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

        # Execute the division allocation query
        query = text("""
            WITH sales_norm AS (
              SELECT
                CASE WHEN s.derived_customer_class = 'Hospitality'
                     THEN NULLIF(TRIM(s.flag),'')
                     ELSE NULLIF(TRIM(s.customer_name),'')
                END                            AS group_key,
                CASE WHEN s.derived_customer_class LIKE 'Hospitality%' THEN 'Hospitality'
                     ELSE s.derived_customer_class
                END                            AS customer_class,
                s.item_division,
                s.ext_sales,
                s.period
              FROM dfm_dashboards.sales s
              WHERE YEAR(s.period)=2025
            ),
            grouped_sales AS (           -- collapse sales by group_key + division
              SELECT
                group_key, customer_class, item_division,
                SUM(ext_sales) AS total_sales
              FROM sales_norm
              WHERE group_key IS NOT NULL
              GROUP BY group_key, customer_class, item_division
            ),
            group_totals AS (            -- totals per group
              SELECT group_key, customer_class, SUM(total_sales) AS total_group_sales
              FROM grouped_sales
              GROUP BY group_key, customer_class
            ),
            ratios_raw AS (              -- raw ratios (may still have dupes from dirty data)
              SELECT
                gs.group_key, gs.customer_class, gs.item_division,
                CASE WHEN gt.total_group_sales=0 THEN 0
                     ELSE gs.total_sales/gt.total_group_sales END AS division_ratio_2025
              FROM grouped_sales gs
              JOIN group_totals gt
                ON gt.group_key=gs.group_key
               AND gt.customer_class=gs.customer_class
            ),
            ratios AS (                  -- HARD DEDUPE ratios
              SELECT
                group_key, customer_class, item_division,
                MAX(division_ratio_2025) AS division_ratio_2025
              FROM ratios_raw
              GROUP BY group_key, customer_class, item_division
            ),
            budget_norm AS (
              SELECT
                b.salesperson_id,
                b.salesperson_name,
                CASE WHEN b.customer_class LIKE 'Hospitality%' THEN 'Hospitality'
                     ELSE b.customer_class END            AS customer_class,
                CASE WHEN b.customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(b.flag),'')
                     ELSE NULLIF(TRIM(b.customer_name),'') END AS group_key,
                b.quarter_1_sales, b.quarter_2_sales, b.quarter_3_sales, b.quarter_4_sales
              FROM dfm_dashboards.budget_2026 b
              WHERE b.is_custom=0
            ),
            collapsed_budget AS (        -- collapse per salesperson + group_key
              SELECT
                salesperson_id, salesperson_name, customer_class, group_key,
                SUM(quarter_1_sales) AS q1_total,
                SUM(quarter_2_sales) AS q2_total,
                SUM(quarter_3_sales) AS q3_total,
                SUM(quarter_4_sales) AS q4_total
              FROM budget_norm
              WHERE group_key IS NOT NULL
              GROUP BY salesperson_id, salesperson_name, customer_class, group_key
            ),
            divisions_dedup AS (         -- guard against duplicate div_no rows
              SELECT d.div_no, MIN(d.div_desc) AS div_desc
              FROM dfm_dashboards.division_masters d
              GROUP BY d.div_no
            )
            SELECT
              b.salesperson_id, b.salesperson_name, b.customer_class, b.group_key,
              d.div_no AS item_division, d.div_desc AS division_name,
              ROUND(b.q1_total * r.division_ratio_2025, 2) AS q1_allocated,
              ROUND(b.q2_total * r.division_ratio_2025, 2) AS q2_allocated,
              ROUND(b.q3_total * r.division_ratio_2025, 2) AS q3_allocated,
              ROUND(b.q4_total * r.division_ratio_2025, 2) AS q4_allocated,
              ROUND((b.q1_total+b.q2_total+b.q3_total+b.q4_total)*r.division_ratio_2025, 2) AS total_allocated,
              r.division_ratio_2025
            FROM collapsed_budget b
            JOIN ratios r
              ON r.group_key=b.group_key
             AND r.customer_class=b.customer_class
            JOIN divisions_dedup d
              ON d.div_no=r.item_division
            ORDER BY b.customer_class, b.salesperson_name, b.group_key, d.div_no
        """)

        result = db.exec(query)
        division_data = []
        
        for row in result:
            division_data.append({
                "salesperson_id": row.salesperson_id,
                "salesperson_name": row.salesperson_name,
                "customer_class": row.customer_class,
                "group_key": row.group_key,
                "item_division": row.item_division,
                "division_name": row.division_name,
                "q1_allocated": float(row.q1_allocated) if row.q1_allocated else 0.0,
                "q2_allocated": float(row.q2_allocated) if row.q2_allocated else 0.0,
                "q3_allocated": float(row.q3_allocated) if row.q3_allocated else 0.0,
                "q4_allocated": float(row.q4_allocated) if row.q4_allocated else 0.0,
                "total_allocated": float(row.total_allocated) if row.total_allocated else 0.0,
                "division_ratio_2025": float(row.division_ratio_2025) if row.division_ratio_2025 else 0.0
            })

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
