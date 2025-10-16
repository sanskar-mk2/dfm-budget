from sqlmodel import Session, text, select
from typing import List, Dict, Any
from db.budget_models import DivisionRatioOverride
from datetime import datetime


class DivisionService:
    def __init__(self, db: Session):
        self.db = db

    def get_division_allocations(self) -> List[Dict[str, Any]]:
        """
        Get division allocations with custom ratio overrides applied
        """
        query = text(
            """
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
                CASE WHEN b.customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(b.brand),'')
                     ELSE NULL END AS brand,
                b.quarter_1_sales, b.quarter_2_sales, b.quarter_3_sales, b.quarter_4_sales
              FROM dfm_dashboards.budget_2026 b
              WHERE b.is_custom=0
            ),
            collapsed_budget AS (        -- collapse per salesperson + group_key
              SELECT
                salesperson_id, salesperson_name, customer_class, group_key,
                MAX(brand) AS brand,
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
              b.salesperson_id, b.salesperson_name, b.customer_class, b.group_key, b.brand,
              d.div_no AS item_division, d.div_desc AS division_name,
              COALESCE(o.custom_ratio, r.division_ratio_2025) AS effective_ratio,
              CASE WHEN o.custom_ratio IS NOT NULL THEN 1 ELSE 0 END AS is_custom,
              ROUND(b.q1_total * COALESCE(o.custom_ratio, r.division_ratio_2025), 2) AS q1_allocated,
              ROUND(b.q2_total * COALESCE(o.custom_ratio, r.division_ratio_2025), 2) AS q2_allocated,
              ROUND(b.q3_total * COALESCE(o.custom_ratio, r.division_ratio_2025), 2) AS q3_allocated,
              ROUND(b.q4_total * COALESCE(o.custom_ratio, r.division_ratio_2025), 2) AS q4_allocated,
              ROUND((b.q1_total+b.q2_total+b.q3_total+b.q4_total)*COALESCE(o.custom_ratio, r.division_ratio_2025), 2) AS total_allocated,
              r.division_ratio_2025
            FROM collapsed_budget b
            JOIN ratios r
              ON r.group_key=b.group_key
             AND r.customer_class=b.customer_class
            JOIN divisions_dedup d
              ON d.div_no=r.item_division
            LEFT JOIN division_ratio_overrides o
              ON o.salesperson_id=b.salesperson_id
             AND o.customer_class=b.customer_class
             AND o.group_key=b.group_key
             AND o.item_division=d.div_no
            ORDER BY b.customer_class, b.salesperson_name, b.group_key, d.div_no
        """
        )

        result = self.db.exec(query)
        division_data = []

        for row in result:
            division_data.append(
                {
                    "salesperson_id": row.salesperson_id,
                    "salesperson_name": row.salesperson_name,
                    "customer_class": row.customer_class,
                    "group_key": row.group_key,
                    "brand": row.brand,
                    "item_division": row.item_division,
                    "division_name": row.division_name,
                    "effective_ratio": (
                        float(row.effective_ratio) if row.effective_ratio else 0.0
                    ),
                    "is_custom": bool(row.is_custom),
                    "q1_allocated": (
                        float(row.q1_allocated) if row.q1_allocated else 0.0
                    ),
                    "q2_allocated": (
                        float(row.q2_allocated) if row.q2_allocated else 0.0
                    ),
                    "q3_allocated": (
                        float(row.q3_allocated) if row.q3_allocated else 0.0
                    ),
                    "q4_allocated": (
                        float(row.q4_allocated) if row.q4_allocated else 0.0
                    ),
                    "total_allocated": (
                        float(row.total_allocated) if row.total_allocated else 0.0
                    ),
                    "division_ratio_2025": (
                        float(row.division_ratio_2025)
                        if row.division_ratio_2025
                        else 0.0
                    ),
                }
            )

        return division_data

    def save_ratio_overrides(self, overrides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save custom ratio overrides for divisions
        """
        try:
            saved_count = 0
            updated_count = 0

            for override in overrides:
                # Check if override already exists
                existing = self.db.exec(
                    select(DivisionRatioOverride).where(
                        DivisionRatioOverride.salesperson_id
                        == override["salesperson_id"],
                        DivisionRatioOverride.customer_class
                        == override["customer_class"],
                        DivisionRatioOverride.group_key == override["group_key"],
                        DivisionRatioOverride.item_division
                        == override["item_division"],
                    )
                ).first()

                if existing:
                    # Update existing override
                    existing.custom_ratio = override["custom_ratio"]
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new override
                    new_override = DivisionRatioOverride(
                        salesperson_id=override["salesperson_id"],
                        salesperson_name=override["salesperson_name"],
                        customer_class=override["customer_class"],
                        group_key=override["group_key"],
                        item_division=override["item_division"],
                        custom_ratio=override["custom_ratio"],
                    )
                    self.db.add(new_override)
                    saved_count += 1

            self.db.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "updated_count": updated_count,
                "total_processed": len(overrides),
            }

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_ratio_override(
        self,
        salesperson_id: int,
        customer_class: str,
        group_key: str,
        item_division: int,
    ) -> bool:
        """
        Delete a custom ratio override (reset to default)
        """
        try:
            override = self.db.exec(
                select(DivisionRatioOverride).where(
                    DivisionRatioOverride.salesperson_id == salesperson_id,
                    DivisionRatioOverride.customer_class == customer_class,
                    DivisionRatioOverride.group_key == group_key,
                    DivisionRatioOverride.item_division == item_division,
                )
            ).first()

            if override:
                self.db.delete(override)
                self.db.commit()
                return True
            return False

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_group_overrides(
        self, salesperson_id: int, customer_class: str, group_key: str
    ) -> int:
        """
        Delete all custom ratio overrides for a specific group
        """
        try:
            result = self.db.exec(
                text(
                    """
                    DELETE FROM division_ratio_overrides 
                    WHERE salesperson_id = :salesperson_id 
                    AND customer_class = :customer_class 
                    AND group_key = :group_key
                """
                ).bindparams(
                    salesperson_id=salesperson_id,
                    customer_class=customer_class,
                    group_key=group_key,
                )
            )
            self.db.commit()
            return result.rowcount

        except Exception as e:
            self.db.rollback()
            raise e

    def reset_all_overrides(self) -> int:
        """
        Reset all custom ratio overrides
        """
        try:
            result = self.db.exec(text("DELETE FROM division_ratio_overrides"))
            self.db.commit()
            return result.rowcount

        except Exception as e:
            self.db.rollback()
            raise e
