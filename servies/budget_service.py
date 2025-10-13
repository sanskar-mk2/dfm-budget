from sqlmodel import Session, select, text
from typing import List, Dict, Any, Optional
from db.budget_models import Budget
from db.dfm_reflect import Salesperson


class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def get_budgets_by_salesperson(self, salesperson_id: int) -> List[Dict[str, Any]]:
        """Get all budgets for a specific salesperson"""
        query = select(Budget).where(Budget.salesperson_id == salesperson_id)
        budgets = self.db.exec(query).all()
        
        return [
            {
                "id": budget.id,
                "salesperson_id": budget.salesperson_id,
                "salesperson_name": budget.salesperson_name,
                "brand": budget.brand,
                "flag": budget.flag,
                "customer_name": budget.customer_name,
                "customer_class": budget.customer_class,
                "quarter_1_sales": budget.quarter_1_sales,
                "quarter_2_sales": budget.quarter_2_sales,
                "quarter_3_sales": budget.quarter_3_sales,
                "quarter_4_sales": budget.quarter_4_sales,
                "is_custom": budget.is_custom,
                "total_sales": budget.quarter_1_sales + budget.quarter_2_sales + 
                              budget.quarter_3_sales + budget.quarter_4_sales
            }
            for budget in budgets
        ]

    def create_budget(self, budget_data: Dict[str, Any]) -> Budget:
        """Create a new budget entry"""
        budget = Budget(**budget_data)
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def update_budget(self, budget_id: int, budget_data: Dict[str, Any]) -> Optional[Budget]:
        """Update an existing budget entry"""
        budget = self.db.get(Budget, budget_id)
        if not budget:
            return None
        
        for key, value in budget_data.items():
            if hasattr(budget, key):
                setattr(budget, key, value)
        
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget entry"""
        budget = self.db.get(Budget, budget_id)
        if not budget:
            return False
        
        self.db.delete(budget)
        self.db.commit()
        return True

    def generate_budget_from_sales(self, salesperson_id: int, salesperson_name: str, 
                                 sales_data: List[Dict[str, Any]]) -> List[Budget]:
        """Generate budget entries from sales data"""
        budgets = []
        
        for sale in sales_data:
            budget = Budget(
                salesperson_id=salesperson_id,
                salesperson_name=salesperson_name,
                brand=sale.get('brand'),
                flag=sale.get('flag'),
                customer_name=sale.get('customer_name'),
                customer_class=sale.get('derived_customer_class'),
                quarter_1_sales=float(sale.get('q1_sales', 0)),
                quarter_2_sales=float(sale.get('q2_sales', 0)),
                quarter_3_sales=float(sale.get('q3_sales', 0)),
                quarter_4_sales=float(sale.get('q4_sales', 0)),
                is_custom=False
            )
            budgets.append(budget)
        
        return budgets

    def get_budget_summary(self, salesperson_id: int) -> Dict[str, Any]:
        """Get budget summary for a salesperson"""
        budgets = self.get_budgets_by_salesperson(salesperson_id)
        
        if not budgets:
            return {
                "total_budgets": 0,
                "total_q1": 0,
                "total_q2": 0,
                "total_q3": 0,
                "total_q4": 0,
                "total_sales": 0,
                "custom_budgets": 0
            }
        
        total_q1 = sum(budget['quarter_1_sales'] for budget in budgets)
        total_q2 = sum(budget['quarter_2_sales'] for budget in budgets)
        total_q3 = sum(budget['quarter_3_sales'] for budget in budgets)
        total_q4 = sum(budget['quarter_4_sales'] for budget in budgets)
        total_sales = total_q1 + total_q2 + total_q3 + total_q4
        custom_budgets = sum(1 for budget in budgets if budget['is_custom'])
        
        return {
            "total_budgets": len(budgets),
            "total_q1": total_q1,
            "total_q2": total_q2,
            "total_q3": total_q3,
            "total_q4": total_q4,
            "total_sales": total_sales,
            "custom_budgets": custom_budgets
        }

    def get_unique_customer_classes(self) -> List[str]:
        """Get all unique customer classes from entire sales database for autosuggest"""
        query = text("""
            SELECT DISTINCT derived_customer_class
            FROM sales 
            WHERE derived_customer_class IS NOT NULL
              AND derived_customer_class != ''
            ORDER BY derived_customer_class
        """)
        
        result = self.db.exec(query)
        return [row[0] for row in result if row[0]]

    def get_unique_brands(self) -> List[str]:
        """Get all unique brands from entire sales database for hospitality users"""
        query = text("""
            SELECT DISTINCT brand
            FROM sales 
            WHERE brand IS NOT NULL
              AND brand != ''
            ORDER BY brand
        """)
        
        result = self.db.exec(query)
        return [row[0] for row in result if row[0]]
