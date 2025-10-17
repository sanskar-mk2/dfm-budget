from sqlmodel import Session, text, select
from typing import List, Dict, Any
from datetime import datetime
from db.budget_models import GrossProfitOverride


class GrossProfitService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # MAIN QUERY
    # ------------------------------------------------------------------
    def get_gross_profit_allocations(self) -> List[Dict[str, Any]]:
        """
        Compute gross-profit % (from 2025 actuals) and apply to 2026 budget,
        merging any manual gp_ratio_overrides.
        Returns one record per group (class + salesperson + group_key)
        with quarterly and total GP$ projections.
        """
        query = text(
            """
            WITH gp AS (
              /* --- GP% logic from Step B --- */
              SELECT
                grp.group_key,
                grp.customer_class,
                ROUND(IF(grp.q1_sales = 0,
                  IFNULL(
                    1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
                        / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
                    NULL),
                  1 - (grp.q1_cost / grp.q1_sales)
                ),6) AS q1_gp_percent,
                ROUND(IF(grp.q2_sales = 0,
                  IFNULL(
                    1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
                        / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
                    NULL),
                  1 - (grp.q2_cost / grp.q2_sales)
                ),6) AS q2_gp_percent,
                ROUND(IF(grp.q3_sales = 0,
                  IFNULL(
                    1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
                        / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
                    NULL),
                  1 - (grp.q3_cost / grp.q3_sales)
                ),6) AS q3_gp_percent,
                ROUND(IF(grp.q4_sales = 0,
                  IFNULL(
                    1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
                        / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
                    NULL),
                  1 - (grp.q4_cost / grp.q4_sales)
                ),6) AS q4_gp_percent,
                ROUND(
                  IF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales)=0,NULL,
                    1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
                        /(grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales))
                  ),6
                ) AS full_year_gp_percent
              FROM (
                SELECT
                  IF(s.derived_customer_class='Hospitality', s.flag, s.customer_name) AS group_key,
                  s.derived_customer_class AS customer_class,
                  SUM(IF(MONTH(s.period) BETWEEN 1 AND 3, s.ext_sales, 0)) AS q1_sales,
                  SUM(IF(MONTH(s.period) BETWEEN 1 AND 3, s.ext_cost,  0)) AS q1_cost,
                  SUM(IF(MONTH(s.period) BETWEEN 4 AND 6, s.ext_sales, 0)) AS q2_sales,
                  SUM(IF(MONTH(s.period) BETWEEN 4 AND 6, s.ext_cost,  0)) AS q2_cost,
                  SUM(IF(MONTH(s.period) BETWEEN 7 AND 9, s.ext_sales, 0)) AS q3_sales,
                  SUM(IF(MONTH(s.period) BETWEEN 7 AND 9, s.ext_cost,  0)) AS q3_cost,
                  SUM(IF(MONTH(s.period) BETWEEN 10 AND 12, s.ext_sales, 0)) AS q4_sales,
                  SUM(IF(MONTH(s.period) BETWEEN 10 AND 12, s.ext_cost,  0)) AS q4_cost
                FROM dfm_dashboards.sales s
                JOIN (
                  SELECT so.order_no
                  FROM dfm_dashboards.sales so
                  WHERE YEAR(so.period)=2025
                  GROUP BY so.order_no
                  HAVING SUM(so.qty)>=0 AND SUM(so.is_warranty='yes')=0
                ) vo ON vo.order_no = s.order_no
                WHERE YEAR(s.period)=2025
                  AND (
                    (s.derived_customer_class='Hospitality' AND s.flag IS NOT NULL AND s.flag<>'')
                    OR (s.derived_customer_class<>'Hospitality' AND s.customer_name IS NOT NULL AND s.customer_name<>'')
                  )
                GROUP BY IF(s.derived_customer_class='Hospitality', s.flag, s.customer_name),
                         s.derived_customer_class
              ) grp
            )
            SELECT
              b.salesperson_id,
              b.salesperson_name,
              b.customer_class,
              IF(b.customer_class='Hospitality', b.flag, b.customer_name) AS group_key,
              /* derive brand for hospitality */
              CASE WHEN b.customer_class LIKE 'Hospitality%' THEN b.brand ELSE NULL END AS brand,

              b.quarter_1_sales,
              b.quarter_2_sales,
              b.quarter_3_sales,
              b.quarter_4_sales,

              g.q1_gp_percent,
              g.q2_gp_percent,
              g.q3_gp_percent,
              g.q4_gp_percent,
              g.full_year_gp_percent,

              COALESCE(o.custom_gp_percent, g.full_year_gp_percent) AS effective_gp_percent,
              CASE WHEN o.custom_gp_percent IS NOT NULL THEN 1 ELSE 0 END AS is_custom,

              ROUND(b.quarter_1_sales * COALESCE(o.custom_gp_percent, g.full_year_gp_percent),2) AS q1_gp_value,
              ROUND(b.quarter_2_sales * COALESCE(o.custom_gp_percent, g.full_year_gp_percent),2) AS q2_gp_value,
              ROUND(b.quarter_3_sales * COALESCE(o.custom_gp_percent, g.full_year_gp_percent),2) AS q3_gp_value,
              ROUND(b.quarter_4_sales * COALESCE(o.custom_gp_percent, g.full_year_gp_percent),2) AS q4_gp_value,
              ROUND(
                (b.quarter_1_sales + b.quarter_2_sales + b.quarter_3_sales + b.quarter_4_sales)
                * COALESCE(o.custom_gp_percent, g.full_year_gp_percent),2
              ) AS total_gp_value
            FROM dfm_dashboards.budget_2026 b
            LEFT JOIN gp g
              ON g.group_key = IF(b.customer_class='Hospitality', b.flag, b.customer_name)
             AND g.customer_class = b.customer_class
            LEFT JOIN gp_ratio_overrides o
              ON o.salesperson_id = b.salesperson_id
             AND o.customer_class = b.customer_class
             AND o.group_key = IF(b.customer_class='Hospitality', b.flag, b.customer_name)
            WHERE b.is_custom = 0
            ORDER BY b.customer_class, b.salesperson_name, group_key;
            """
        )

        result = self.db.exec(query)
        return [dict(row._mapping) for row in result]

    # ------------------------------------------------------------------
    # SAVE / RESET OVERRIDES
    # ------------------------------------------------------------------
    def save_gp_overrides(self, overrides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save or update GP% overrides (one per group).
        """
        saved, updated = 0, 0
        for o in overrides:
            existing = self.db.exec(
                select(GrossProfitOverride).where(
                    GrossProfitOverride.salesperson_id == o["salesperson_id"],
                    GrossProfitOverride.customer_class == o["customer_class"],
                    GrossProfitOverride.group_key == o["group_key"],
                )
            ).first()

            if existing:
                existing.custom_gp_percent = o["custom_gp_percent"]
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                self.db.add(GrossProfitOverride(**o))
                saved += 1

        self.db.commit()
        return {"saved": saved, "updated": updated}

    def delete_gp_override(
        self, salesperson_id: int, customer_class: str, group_key: str
    ) -> int:
        """
        Reset (delete) the override for a single group.
        """
        result = self.db.exec(
            text(
                """
                DELETE FROM gp_ratio_overrides
                WHERE salesperson_id=:sid
                  AND customer_class=:cc
                  AND group_key=:gk
                """
            ).bindparams(sid=salesperson_id, cc=customer_class, gk=group_key)
        )
        self.db.commit()
        return result.rowcount
