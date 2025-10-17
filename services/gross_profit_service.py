from sqlmodel import Session, text
from typing import List, Dict, Any


class GrossProfitService:
    def __init__(self, db: Session):
        self.db = db

    def get_gross_profit_allocations(self) -> List[Dict[str, Any]]:
        query = text(
            """
WITH gp AS (
  /* ---- your gp% logic from Step B (already debugged & fallbacked) ---- */
  SELECT
    grp.group_key,
    grp.customer_class,
    ROUND(IF(grp.q1_sales = 0,
      IFNULL(
        1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
              / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
        NULL),
      1 - (grp.q1_cost / grp.q1_sales)),6) AS q1_gp_percent,
    ROUND(IF(grp.q2_sales = 0,
      IFNULL(
        1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
              / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
        NULL),
      1 - (grp.q2_cost / grp.q2_sales)),6) AS q2_gp_percent,
    ROUND(IF(grp.q3_sales = 0,
      IFNULL(
        1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
              / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
        NULL),
      1 - (grp.q3_cost / grp.q3_sales)),6) AS q3_gp_percent,
    ROUND(IF(grp.q4_sales = 0,
      IFNULL(
        1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
              / NULLIF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales),0)),
        NULL),
      1 - (grp.q4_cost / grp.q4_sales)),6) AS q4_gp_percent,
    ROUND(
      IF((grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales)=0,NULL,
        1 - ((grp.q1_cost + grp.q2_cost + grp.q3_cost + grp.q4_cost)
            /(grp.q1_sales + grp.q2_sales + grp.q3_sales + grp.q4_sales))),6)
      AS full_year_gp_percent
  FROM (
    SELECT
      IF(s.derived_customer_class='Hospitality',s.flag,s.customer_name) AS group_key,
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
      HAVING SUM(so.qty)>=0
         AND SUM(so.is_warranty='yes')=0
    ) vo ON vo.order_no=s.order_no
    WHERE YEAR(s.period)=2025
      AND ((s.derived_customer_class='Hospitality' AND s.flag IS NOT NULL AND s.flag<>'')
        OR (s.derived_customer_class<>'Hospitality' AND s.customer_name IS NOT NULL AND s.customer_name<>'' ))
    GROUP BY IF(s.derived_customer_class='Hospitality',s.flag,s.customer_name),
             s.derived_customer_class
  ) grp
)
SELECT
  b.salesperson_id,
  b.salesperson_name,
  b.customer_class,
  IF(b.customer_class='Hospitality', b.flag, b.customer_name) AS group_key,
  b.quarter_1_sales,
  b.quarter_2_sales,
  b.quarter_3_sales,
  b.quarter_4_sales,

  /* attach gp% */
  g.q1_gp_percent,
  g.q2_gp_percent,
  g.q3_gp_percent,
  g.q4_gp_percent,
  g.full_year_gp_percent,

  /* estimated gross profit dollars for each quarter */
  ROUND(b.quarter_1_sales * IFNULL(g.q1_gp_percent,g.full_year_gp_percent),2) AS q1_gp_value,
  ROUND(b.quarter_2_sales * IFNULL(g.q2_gp_percent,g.full_year_gp_percent),2) AS q2_gp_value,
  ROUND(b.quarter_3_sales * IFNULL(g.q3_gp_percent,g.full_year_gp_percent),2) AS q3_gp_value,
  ROUND(b.quarter_4_sales * IFNULL(g.q4_gp_percent,g.full_year_gp_percent),2) AS q4_gp_value,
  ROUND(
    (b.quarter_1_sales+b.quarter_2_sales+b.quarter_3_sales+b.quarter_4_sales)
     * IFNULL(g.full_year_gp_percent,0),2) AS total_gp_value
FROM dfm_dashboards.budget_2026 b
LEFT JOIN gp g
  ON g.group_key = IF(b.customer_class='Hospitality', b.flag, b.customer_name)
 AND g.customer_class = b.customer_class
WHERE b.is_custom=0
ORDER BY b.customer_class, b.salesperson_name, group_key;

        """
        )

        result = self.db.exec(query)
        return [dict(row._mapping) for row in result]
