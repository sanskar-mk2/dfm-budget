from sqlmodel import Session, select, text
from db.dfm_reflect import Users
from db.budget_models import Budget
from typing import List, Dict, Any
from constants import SUPERADMIN, ADMIN


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all salespeople with their sales and budget data
        """
        # Get all salespeople (exclude admins - those with salesman_id = 0 or null)
        salespeople_query = text(
            """
            SELECT DISTINCT s.salesman_no, s.salesman_name, s.role
            FROM salesperson_masters s
            INNER JOIN users u ON u.salesman_id = s.salesman_no
            WHERE u.salesman_id IS NOT NULL AND u.salesman_id != 0
            ORDER BY s.salesman_no
        """
        )

        salespeople_result = self.db.exec(salespeople_query)
        salespeople_data = [dict(row._mapping) for row in salespeople_result]

        summary_data = []

        for salesperson in salespeople_data:
            salesman_no = salesperson["salesman_no"]
            salesman_name = salesperson["salesman_name"]
            role = salesperson["role"] or "Unknown"

            # Get sales data (Q1-Q3 from sales table, Q4 from open_orders)
            sales_data = self._get_salesperson_sales_data(salesman_no)

            # Get budget data
            budget_data = self._get_salesperson_budget_data(salesman_no)

            # Calculate totals - convert to float to ensure consistent types with null safety
            total_sales = (
                float(sales_data["q1_sales"] or 0)
                + float(sales_data["q2_sales"] or 0)
                + float(sales_data["q3_sales"] or 0)
                + float(sales_data["q4_sales"] or 0)
            )
            total_budget = (
                float(budget_data["q1_budget"] or 0)
                + float(budget_data["q2_budget"] or 0)
                + float(budget_data["q3_budget"] or 0)
                + float(budget_data["q4_budget"] or 0)
            )
            variance = total_sales - total_budget

            summary_data.append(
                {
                    "salesperson_id": salesman_no,
                    "salesperson_name": salesman_name,
                    "role": role,
                    "q1_sales": float(sales_data["q1_sales"] or 0),
                    "q2_sales": float(sales_data["q2_sales"] or 0),
                    "q3_sales": float(sales_data["q3_sales"] or 0),
                    "q4_sales": float(sales_data["q4_sales"] or 0),
                    "q4_orders": float(sales_data["q4_orders"] or 0),
                    "open_2026": float(sales_data["open_2026"] or 0),
                    "total_sales": total_sales,
                    "zero_perc_sales": float(sales_data["zero_perc_sales"] or 0),
                    "zero_perc_sales_percent": float(
                        sales_data["zero_perc_sales_percent"] or 0
                    ),
                    "q1_budget": float(budget_data["q1_budget"] or 0),
                    "q2_budget": float(budget_data["q2_budget"] or 0),
                    "q3_budget": float(budget_data["q3_budget"] or 0),
                    "q4_budget": float(budget_data["q4_budget"] or 0),
                    "total_budget": total_budget,
                    "variance": variance,
                }
            )

        # Sort by total sales descending
        summary_data.sort(key=lambda x: x["total_sales"], reverse=True)

        return summary_data

    def _get_salesperson_sales_data(self, salesman_no: int) -> Dict[str, Any]:
        """Get sales data for a specific salesperson"""

        # Q1-Q4 sales from sales table
        q1_q4_query = text(
            f"""
            SELECT 
                SUM(CASE WHEN period >= '2025-01-01' AND period < '2025-04-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q1_sales,
                SUM(CASE WHEN period >= '2025-04-01' AND period < '2025-07-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q2_sales,
                SUM(CASE WHEN period >= '2025-07-01' AND period < '2025-10-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q3_sales,
                SUM(CASE WHEN period >= '2025-10-01' AND period < '2026-01-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as zero_perc_sales_q1_q4
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
        """
        )

        q1_q4_result = self.db.exec(q1_q4_query).first()
        q1_q4_data = (
            dict(q1_q4_result._mapping)
            if q1_q4_result
            else {
                "q1_sales": 0,
                "q2_sales": 0,
                "q3_sales": 0,
                "q4_sales": 0,
                "zero_perc_sales_q1_q4": 0,
            }
        )

        # Q4 orders from open_orders table
        q4_orders_query = text(
            f"""
            SELECT 
                SUM(COALESCE(ext_sales, 0)) as q4_orders,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_orders_zero_perc_sales
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2025-10-01' 
              AND requested_ship_date < '2026-01-01'
        """
        )

        q4_orders_result = self.db.exec(q4_orders_query).first()
        q4_orders_data = (
            dict(q4_orders_result._mapping)
            if q4_orders_result
            else {"q4_orders": 0, "q4_orders_zero_perc_sales": 0}
        )

        # 2026 open orders
        open_2026_query = text(
            f"""
            SELECT 
                SUM(COALESCE(ext_sales, 0)) as open_2026
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2026-01-01' 
              AND requested_ship_date < '2027-01-01'
        """
        )

        open_2026_result = self.db.exec(open_2026_query).first()
        open_2026_data = (
            dict(open_2026_result._mapping) if open_2026_result else {"open_2026": 0}
        )

        # Calculate totals with null safety
        q1_sales = q1_q4_data["q1_sales"] or 0
        q2_sales = q1_q4_data["q2_sales"] or 0
        q3_sales = q1_q4_data["q3_sales"] or 0
        q4_sales = q1_q4_data["q4_sales"] or 0
        q4_orders = q4_orders_data["q4_orders"] or 0
        zero_perc_q1_q4 = q1_q4_data["zero_perc_sales_q1_q4"] or 0
        zero_perc_q4_orders = q4_orders_data["q4_orders_zero_perc_sales"] or 0

        total_sales = q1_sales + q2_sales + q3_sales + q4_sales + q4_orders
        total_zero_perc_sales = zero_perc_q1_q4 + zero_perc_q4_orders
        zero_perc_sales_percent = (
            (total_zero_perc_sales / total_sales * 100) if total_sales > 0 else 0
        )

        return {
            "q1_sales": float(q1_sales),
            "q2_sales": float(q2_sales),
            "q3_sales": float(q3_sales),
            "q4_sales": float(q4_sales),
            "q4_orders": float(q4_orders),
            "open_2026": float(open_2026_data["open_2026"] or 0),
            "zero_perc_sales": float(total_zero_perc_sales),
            "zero_perc_sales_percent": round(float(zero_perc_sales_percent), 2),
        }

    def _get_salesperson_budget_data(self, salesman_no: int) -> Dict[str, Any]:
        """Get budget data for a specific salesperson"""

        # Use ORM approach like the existing budget service
        query = select(Budget).where(Budget.salesperson_id == salesman_no)
        budgets = self.db.exec(query).all()

        if not budgets:
            return {"q1_budget": 0, "q2_budget": 0, "q3_budget": 0, "q4_budget": 0}

        # Sum up all budget entries for this salesperson with null safety
        q1_budget = sum(budget.quarter_1_sales or 0 for budget in budgets)
        q2_budget = sum(budget.quarter_2_sales or 0 for budget in budgets)
        q3_budget = sum(budget.quarter_3_sales or 0 for budget in budgets)
        q4_budget = sum(budget.quarter_4_sales or 0 for budget in budgets)

        return {
            "q1_budget": float(q1_budget),
            "q2_budget": float(q2_budget),
            "q3_budget": float(q3_budget),
            "q4_budget": float(q4_budget),
        }

    def is_admin(self, username: str) -> bool:
        """Check if user is an admin (salesman_id = 0 or null)"""
        user = self.db.exec(select(Users).where(Users.username == username)).first()
        if not user:
            return False

        return user.salesman_id == SUPERADMIN or user.salesman_id is ADMIN
