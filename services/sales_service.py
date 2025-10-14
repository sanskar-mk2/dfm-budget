from sqlmodel import Session, select, text
from db.dfm_reflect import Salesperson
from typing import List, Dict, Any


class SalesService:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_data(self, username: str) -> List[Dict[str, Any]]:
        """
        Get sales data based on user's salesperson role
        """
        # Get user's salesperson info
        user_salesperson = self._get_user_salesperson(username)

        if not user_salesperson:
            return []

        # Check if user is hospitality or non-hospitality
        role = user_salesperson.role or ""
        is_hospitality = role.startswith("Hospitality")

        if is_hospitality:
            return self._get_hospitality_sales_data(user_salesperson.salesman_no)
        else:
            return self._get_non_hospitality_sales_data(user_salesperson.salesman_no)

    def _get_user_salesperson(self, username: str):
        """Get salesperson info for the user"""
        from db.dfm_reflect import Users

        # Get user
        user = self.db.exec(select(Users).where(Users.username == username)).first()
        if not user or not user.salesman_id:
            return None

        # Get salesperson
        salesperson = self.db.exec(
            select(Salesperson).where(Salesperson.salesman_no == user.salesman_id)
        ).first()

        return salesperson

    def _get_hospitality_sales_data(self, salesman_no: int) -> List[Dict[str, Any]]:
        """
        Hospitality Salesperson Logic:
        - Group by flag
        - Each flag has a fixed brand
        - derived_customer_class = 'Hospitality'
        """
        # Step 1: Get basic sales data grouped by flag, brand (Q1-Q4 2025 from sales table)
        basic_query = text(
            f"""
            SELECT 
                flag,
                brand,
                SUM(COALESCE(ext_sales, 0)) as total_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as zero_perc_sales_total
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY flag, brand
        """
        )

        basic_result = self.db.exec(basic_query)
        basic_data = [dict(row._mapping) for row in basic_result]

        # Step 2: Get quarterly breakdowns for Q1-Q4 2025
        quarterly_query = text(
            f"""
            SELECT 
                flag,
                brand,
                SUM(CASE WHEN period >= '2025-01-01' AND period < '2025-04-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q1_sales,
                SUM(CASE WHEN period >= '2025-04-01' AND period < '2025-07-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q2_sales,
                SUM(CASE WHEN period >= '2025-07-01' AND period < '2025-10-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q3_sales,
                SUM(CASE WHEN period >= '2025-10-01' AND period < '2026-01-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_sales
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY flag, brand
        """
        )

        quarterly_result = self.db.exec(quarterly_query)
        quarterly_data = {
            f"{row.flag}_{row.brand}": dict(row._mapping) for row in quarterly_result
        }

        # Step 3: Get Q4 data from open_orders (including zero % sales)
        q4_query = text(
            f"""
            SELECT 
                flag,
                brand,
                SUM(COALESCE(ext_sales, 0)) as q4_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_zero_perc_sales
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2025-10-01' 
              AND requested_ship_date < '2026-01-01'
            GROUP BY flag, brand
        """
        )

        q4_result = self.db.exec(q4_query)
        q4_data = {f"{row.flag}_{row.brand}": dict(row._mapping) for row in q4_result}

        # Step 4: Get 2026 open orders data
        open_2026_query = text(
            f"""
            SELECT 
                flag,
                brand,
                SUM(COALESCE(ext_sales, 0)) as open_2026
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2026-01-01' 
              AND requested_ship_date < '2027-01-01'
            GROUP BY flag, brand
        """
        )

        open_2026_result = self.db.exec(open_2026_query)
        open_2026_data = {
            f"{row.flag}_{row.brand}": dict(row._mapping) for row in open_2026_result
        }

        # Step 5: Combine the data
        final_data = []
        for item in basic_data:
            key = f"{item['flag']}_{item['brand']}"
            quarterly = quarterly_data.get(key, {})
            q4 = q4_data.get(key, {})
            open_2026 = open_2026_data.get(key, {})

            total_sales = item["total_sales"]  # This now includes Q1-Q4 from sales table
            zero_perc_total_q1_q4 = item["zero_perc_sales_total"]  # This now includes Q1-Q4 from sales table
            q4_orders = q4.get("q4_sales", 0)  # Q4 orders from open_orders
            q4_orders_zero_perc = q4.get("q4_zero_perc_sales", 0)
            total_sales_with_orders = total_sales + q4_orders
            total_zero_perc_sales = zero_perc_total_q1_q4 + q4_orders_zero_perc
            zero_perc_percent = (
                (total_zero_perc_sales / total_sales_with_orders * 100)
                if total_sales_with_orders > 0
                else 0
            )

            final_data.append(
                {
                    "flag": item["flag"],
                    "brand": item["brand"],
                    "customer_name": None,  # Set to null for hospitality
                    "derived_customer_class": None,  # Set to null for hospitality
                    "q1_sales": quarterly.get("q1_sales", 0),
                    "q2_sales": quarterly.get("q2_sales", 0),
                    "q3_sales": quarterly.get("q3_sales", 0),
                    "q4_sales": quarterly.get("q4_sales", 0),  # Q4 sales from sales table
                    "q4_orders": q4_orders,  # Q4 orders from open_orders
                    "open_2026": open_2026.get("open_2026", 0),
                    "zero_perc_sales_total": total_zero_perc_sales,
                    "total_sales": total_sales_with_orders,
                    "zero_perc_sales_percent": round(zero_perc_percent, 2),
                }
            )

        # Filter out rows with zero total sales
        final_data = [item for item in final_data if (item["total_sales"] or 0) > 0]

        # Sort by brand total sales DESC, flag total sales DESC
        # First, calculate brand totals for sorting
        brand_totals = {}
        flag_totals = {}
        for item in final_data:
            brand = item["brand"] or "Unknown Brand"
            flag = item["flag"] or "Unknown Flag"
            sales = item["total_sales"] or 0

            brand_totals[brand] = brand_totals.get(brand, 0) + sales
            flag_totals[f"{brand}_{flag}"] = (
                flag_totals.get(f"{brand}_{flag}", 0) + sales
            )

        # Sort by brand total sales DESC, flag total sales DESC
        final_data.sort(
            key=lambda x: (
                brand_totals.get(x["brand"] or "Unknown Brand", 0),
                flag_totals.get(
                    f"{x['brand'] or 'Unknown Brand'}_{x['flag'] or 'Unknown Flag'}", 0
                ),
            ),
            reverse=True,
        )
        return final_data

    def _get_non_hospitality_sales_data(self, salesman_no: int) -> List[Dict[str, Any]]:
        """
        Non-Hospitality Salesperson Logic:
        - Group by customer_name
        - derived_customer_class from data
        - brand = NULL, flag = NULL
        """
        # Step 1: Get basic sales data grouped by customer_name, derived_customer_class (Q1-Q4 2025 from sales table)
        basic_query = text(
            f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as total_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as zero_perc_sales_total
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY customer_name, derived_customer_class
        """
        )

        basic_result = self.db.exec(basic_query)
        basic_data = [dict(row._mapping) for row in basic_result]

        # Step 2: Get quarterly breakdowns for Q1-Q4 2025
        quarterly_query = text(
            f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(CASE WHEN period >= '2025-01-01' AND period < '2025-04-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q1_sales,
                SUM(CASE WHEN period >= '2025-04-01' AND period < '2025-07-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q2_sales,
                SUM(CASE WHEN period >= '2025-07-01' AND period < '2025-10-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q3_sales,
                SUM(CASE WHEN period >= '2025-10-01' AND period < '2026-01-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_sales
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY customer_name, derived_customer_class
        """
        )

        quarterly_result = self.db.exec(quarterly_query)
        quarterly_data = {
            f"{row.customer_name}_{row.derived_customer_class}": dict(row._mapping)
            for row in quarterly_result
        }

        # Step 3: Get Q4 data from open_orders (including zero % sales)
        q4_query = text(
            f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as q4_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_zero_perc_sales
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2025-10-01' 
              AND requested_ship_date < '2026-01-01'
            GROUP BY customer_name, derived_customer_class
        """
        )

        q4_result = self.db.exec(q4_query)
        q4_data = {
            f"{row.customer_name}_{row.derived_customer_class}": dict(row._mapping)
            for row in q4_result
        }

        # Step 4: Get 2026 open orders data
        open_2026_query = text(
            f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as open_2026
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2026-01-01' 
              AND requested_ship_date < '2027-01-01'
            GROUP BY customer_name, derived_customer_class
        """
        )

        open_2026_result = self.db.exec(open_2026_query)
        open_2026_data = {
            f"{row.customer_name}_{row.derived_customer_class}": dict(row._mapping)
            for row in open_2026_result
        }

        # Step 5: Combine the data
        final_data = []
        for item in basic_data:
            key = f"{item['customer_name']}_{item['derived_customer_class']}"
            quarterly = quarterly_data.get(key, {})
            q4 = q4_data.get(key, {})
            open_2026 = open_2026_data.get(key, {})

            total_sales = item["total_sales"]  # This now includes Q1-Q4 from sales table
            zero_perc_total_q1_q4 = item["zero_perc_sales_total"]  # This now includes Q1-Q4 from sales table
            q4_orders = q4.get("q4_sales", 0)  # Q4 orders from open_orders
            q4_orders_zero_perc = q4.get("q4_zero_perc_sales", 0)
            total_sales_with_orders = total_sales + q4_orders
            total_zero_perc_sales = zero_perc_total_q1_q4 + q4_orders_zero_perc
            zero_perc_percent = (
                (total_zero_perc_sales / total_sales_with_orders * 100)
                if total_sales_with_orders > 0
                else 0
            )

            final_data.append(
                {
                    "customer_name": item["customer_name"],
                    "derived_customer_class": item["derived_customer_class"],
                    "q1_sales": quarterly.get("q1_sales", 0),
                    "q2_sales": quarterly.get("q2_sales", 0),
                    "q3_sales": quarterly.get("q3_sales", 0),
                    "q4_sales": quarterly.get("q4_sales", 0),  # Q4 sales from sales table
                    "q4_orders": q4_orders,  # Q4 orders from open_orders
                    "open_2026": open_2026.get("open_2026", 0),
                    "zero_perc_sales_total": total_zero_perc_sales,
                    "total_sales": total_sales_with_orders,
                    "zero_perc_sales_percent": round(zero_perc_percent, 2),
                    "brand": None,
                    "flag": None,
                }
            )

        # Filter out rows with zero total sales
        final_data = [item for item in final_data if (item["total_sales"] or 0) > 0]

        # Sort by customer class total sales DESC, customer name total sales DESC
        # First, calculate customer class totals for sorting
        customer_class_totals = {}
        customer_name_totals = {}
        for item in final_data:
            customer_class = item["derived_customer_class"] or "Unknown Class"
            customer_name = item["customer_name"] or "Unknown Customer"
            sales = item["total_sales"] or 0

            customer_class_totals[customer_class] = (
                customer_class_totals.get(customer_class, 0) + sales
            )
            customer_name_totals[f"{customer_class}_{customer_name}"] = (
                customer_name_totals.get(f"{customer_class}_{customer_name}", 0) + sales
            )

        # Sort by customer class total sales DESC, customer name total sales DESC
        final_data.sort(
            key=lambda x: (
                customer_class_totals.get(
                    x["derived_customer_class"] or "Unknown Class", 0
                ),
                customer_name_totals.get(
                    f"{x['derived_customer_class'] or 'Unknown Class'}_{x['customer_name'] or 'Unknown Customer'}",
                    0,
                ),
            ),
            reverse=True,
        )
        return final_data

    def get_sales_summary(self, username: str) -> Dict[str, Any]:
        """
        Get summary statistics for the sales data
        """
        sales_data = self.get_sales_data(username)

        if not sales_data:
            return {
                "total_customers": 0,
                "total_sales": 0,
                "total_q1": 0,
                "total_q2": 0,
                "total_q3": 0,
                "total_q4_sales": 0,
                "total_q4_orders": 0,
                "total_q4": 0,
                "total_open_2026": 0,
                "avg_zero_perc_sales": 0,
            }

        total_customers = len(sales_data)
        total_sales = sum(row.get("total_sales", 0) for row in sales_data)
        total_q1 = sum(row.get("q1_sales", 0) for row in sales_data)
        total_q2 = sum(row.get("q2_sales", 0) for row in sales_data)
        total_q3 = sum(row.get("q3_sales", 0) for row in sales_data)
        total_q4_sales = sum(row.get("q4_sales", 0) for row in sales_data)
        total_q4_orders = sum(row.get("q4_orders", 0) for row in sales_data)
        total_q4 = total_q4_sales + total_q4_orders
        total_open_2026 = sum(row.get("open_2026", 0) for row in sales_data)

        zero_perc_values = [
            row.get("zero_perc_sales_percent", 0)
            for row in sales_data
            if row.get("zero_perc_sales_percent", 0) > 0
        ]
        avg_zero_perc_sales = (
            sum(zero_perc_values) / len(zero_perc_values) if zero_perc_values else 0
        )

        return {
            "total_customers": total_customers,
            "total_sales": total_sales,
            "total_q1": total_q1,
            "total_q2": total_q2,
            "total_q3": total_q3,
            "total_q4_sales": total_q4_sales,
            "total_q4_orders": total_q4_orders,
            "total_q4": total_q4,
            "total_open_2026": total_open_2026,
            "avg_zero_perc_sales": round(avg_zero_perc_sales, 2),
        }

    def get_sales_summary_for_salesperson(
        self, sales_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary statistics for provided sales data (used by admin endpoints)
        """
        if not sales_data:
            return {
                "total_customers": 0,
                "total_sales": 0,
                "total_q1": 0,
                "total_q2": 0,
                "total_q3": 0,
                "total_q4_sales": 0,
                "total_q4_orders": 0,
                "total_q4": 0,
                "total_open_2026": 0,
                "avg_zero_perc_sales": 0,
            }

        total_customers = len(sales_data)
        total_sales = sum(row.get("total_sales", 0) for row in sales_data)
        total_q1 = sum(row.get("q1_sales", 0) for row in sales_data)
        total_q2 = sum(row.get("q2_sales", 0) for row in sales_data)
        total_q3 = sum(row.get("q3_sales", 0) for row in sales_data)
        total_q4_sales = sum(row.get("q4_sales", 0) for row in sales_data)
        total_q4_orders = sum(row.get("q4_orders", 0) for row in sales_data)
        total_q4 = total_q4_sales + total_q4_orders
        total_open_2026 = sum(row.get("open_2026", 0) for row in sales_data)

        zero_perc_values = [
            row.get("zero_perc_sales_percent", 0)
            for row in sales_data
            if row.get("zero_perc_sales_percent", 0) > 0
        ]
        avg_zero_perc_sales = (
            sum(zero_perc_values) / len(zero_perc_values) if zero_perc_values else 0
        )

        return {
            "total_customers": total_customers,
            "total_sales": total_sales,
            "total_q1": total_q1,
            "total_q2": total_q2,
            "total_q3": total_q3,
            "total_q4_sales": total_q4_sales,
            "total_q4_orders": total_q4_orders,
            "total_q4": total_q4,
            "total_open_2026": total_open_2026,
            "avg_zero_perc_sales": round(avg_zero_perc_sales, 2),
        }
