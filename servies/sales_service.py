from sqlmodel import Session, select, text
from db.dfm_reflect import Sales, Orders, Salesperson
from typing import List, Dict, Any
from datetime import datetime


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
        # Step 1: Get basic sales data grouped by flag, brand, customer_name (2025 only)
        basic_query = text(f"""
            SELECT 
                flag,
                brand,
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as total_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as zero_perc_sales_total
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY flag, brand, customer_name, derived_customer_class
        """)
        
        basic_result = self.db.exec(basic_query)
        basic_data = [dict(row._mapping) for row in basic_result]
        
        # Step 2: Get quarterly breakdowns for 2025
        quarterly_query = text(f"""
            SELECT 
                flag,
                brand,
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(CASE WHEN period >= '2025-01-01' AND period < '2025-04-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q1_sales,
                SUM(CASE WHEN period >= '2025-04-01' AND period < '2025-07-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q2_sales,
                SUM(CASE WHEN period >= '2025-07-01' AND period < '2025-10-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q3_sales
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY flag, brand, customer_name, derived_customer_class
        """)
        
        quarterly_result = self.db.exec(quarterly_query)
        quarterly_data = {f"{row.flag}_{row.brand}_{row.customer_name}": dict(row._mapping) for row in quarterly_result}
        
        # Step 3: Get Q4 data from open_orders (including zero % sales)
        q4_query = text(f"""
            SELECT 
                flag,
                brand,
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as q4_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q4_zero_perc_sales
            FROM open_orders 
            WHERE salesperson = {salesman_no}
              AND requested_ship_date >= '2025-10-01' 
              AND requested_ship_date < '2026-01-01'
            GROUP BY flag, brand, customer_name, derived_customer_class
        """)
        
        q4_result = self.db.exec(q4_query)
        q4_data = {f"{row.flag}_{row.brand}_{row.customer_name}": dict(row._mapping) for row in q4_result}
        
        # Step 4: Combine the data
        final_data = []
        for item in basic_data:
            key = f"{item['flag']}_{item['brand']}_{item['customer_name']}"
            quarterly = quarterly_data.get(key, {})
            q4 = q4_data.get(key, {})
            
            total_sales = item['total_sales']
            zero_perc_total_q1_q3 = item['zero_perc_sales_total']
            q4_sales = q4.get('q4_sales', 0)
            q4_zero_perc_sales = q4.get('q4_zero_perc_sales', 0)
            total_sales_with_q4 = total_sales + q4_sales
            total_zero_perc_sales = zero_perc_total_q1_q3 + q4_zero_perc_sales
            zero_perc_percent = (total_zero_perc_sales / total_sales_with_q4 * 100) if total_sales_with_q4 > 0 else 0
            
            final_data.append({
                'flag': item['flag'],
                'brand': item['brand'],
                'customer_name': item['customer_name'],
                'derived_customer_class': item['derived_customer_class'],
                'q1_sales': quarterly.get('q1_sales', 0),
                'q2_sales': quarterly.get('q2_sales', 0),
                'q3_sales': quarterly.get('q3_sales', 0),
                'q4_sales': q4_sales,
                'zero_perc_sales_total': total_zero_perc_sales,
                'total_sales': total_sales_with_q4,
                'zero_perc_sales_percent': round(zero_perc_percent, 2)
            })
        
        # Sort by brand DESC, flag DESC
        final_data.sort(key=lambda x: (x['brand'] or '', x['flag'] or ''), reverse=True)
        return final_data

    def _get_non_hospitality_sales_data(self, salesman_no: int) -> List[Dict[str, Any]]:
        """
        Non-Hospitality Salesperson Logic:
        - Group by customer_name
        - derived_customer_class from data
        - brand = NULL, flag = NULL
        """
        # Step 1: Get basic sales data grouped by customer_name, derived_customer_class (2025 only)
        basic_query = text(f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(COALESCE(ext_sales, 0)) as total_sales,
                SUM(CASE WHEN zero_perc_sales = 'yes' THEN COALESCE(ext_sales, 0) ELSE 0 END) as zero_perc_sales_total
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY customer_name, derived_customer_class
        """)
        
        basic_result = self.db.exec(basic_query)
        basic_data = [dict(row._mapping) for row in basic_result]
        
        # Step 2: Get quarterly breakdowns for 2025
        quarterly_query = text(f"""
            SELECT 
                customer_name,
                COALESCE(derived_customer_class, 'Unknown') as derived_customer_class,
                SUM(CASE WHEN period >= '2025-01-01' AND period < '2025-04-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q1_sales,
                SUM(CASE WHEN period >= '2025-04-01' AND period < '2025-07-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q2_sales,
                SUM(CASE WHEN period >= '2025-07-01' AND period < '2025-10-01' THEN COALESCE(ext_sales, 0) ELSE 0 END) as q3_sales
            FROM sales 
            WHERE salesperson = {salesman_no}
              AND period >= '2025-01-01' AND period < '2026-01-01'
            GROUP BY customer_name, derived_customer_class
        """)
        
        quarterly_result = self.db.exec(quarterly_query)
        quarterly_data = {f"{row.customer_name}_{row.derived_customer_class}": dict(row._mapping) for row in quarterly_result}
        
        # Step 3: Get Q4 data from open_orders (including zero % sales)
        q4_query = text(f"""
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
        """)
        
        q4_result = self.db.exec(q4_query)
        q4_data = {f"{row.customer_name}_{row.derived_customer_class}": dict(row._mapping) for row in q4_result}
        
        # Step 4: Combine the data
        final_data = []
        for item in basic_data:
            key = f"{item['customer_name']}_{item['derived_customer_class']}"
            quarterly = quarterly_data.get(key, {})
            q4 = q4_data.get(key, {})
            
            total_sales = item['total_sales']
            zero_perc_total_q1_q3 = item['zero_perc_sales_total']
            q4_sales = q4.get('q4_sales', 0)
            q4_zero_perc_sales = q4.get('q4_zero_perc_sales', 0)
            total_sales_with_q4 = total_sales + q4_sales
            total_zero_perc_sales = zero_perc_total_q1_q3 + q4_zero_perc_sales
            zero_perc_percent = (total_zero_perc_sales / total_sales_with_q4 * 100) if total_sales_with_q4 > 0 else 0
            
            final_data.append({
                'customer_name': item['customer_name'],
                'derived_customer_class': item['derived_customer_class'],
                'q1_sales': quarterly.get('q1_sales', 0),
                'q2_sales': quarterly.get('q2_sales', 0),
                'q3_sales': quarterly.get('q3_sales', 0),
                'q4_sales': q4_sales,
                'zero_perc_sales_total': total_zero_perc_sales,
                'total_sales': total_sales_with_q4,
                'zero_perc_sales_percent': round(zero_perc_percent, 2),
                'brand': None,
                'flag': None
            })
        
        # Sort by derived_customer_class DESC, customer_name DESC
        final_data.sort(key=lambda x: (x['derived_customer_class'] or '', x['customer_name'] or ''), reverse=True)
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
                "total_q4": 0,
                "avg_zero_perc_sales": 0
            }
        
        total_customers = len(sales_data)
        total_sales = sum(row.get('total_sales', 0) for row in sales_data)
        total_q1 = sum(row.get('q1_sales', 0) for row in sales_data)
        total_q2 = sum(row.get('q2_sales', 0) for row in sales_data)
        total_q3 = sum(row.get('q3_sales', 0) for row in sales_data)
        total_q4 = sum(row.get('q4_sales', 0) for row in sales_data)
        
        zero_perc_values = [row.get('zero_perc_sales_percent', 0) for row in sales_data if row.get('zero_perc_sales_percent', 0) > 0]
        avg_zero_perc_sales = sum(zero_perc_values) / len(zero_perc_values) if zero_perc_values else 0
        
        return {
            "total_customers": total_customers,
            "total_sales": total_sales,
            "total_q1": total_q1,
            "total_q2": total_q2,
            "total_q3": total_q3,
            "total_q4": total_q4,
            "avg_zero_perc_sales": round(avg_zero_perc_sales, 2)
        }
