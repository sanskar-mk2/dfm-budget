from sqlalchemy.ext.automap import automap_base
from .core import engine

DFMBase = automap_base()
DFMBase.prepare(autoload_with=engine)

Sales = getattr(DFMBase.classes, "sales_budget_2026", None)
Users = DFMBase.classes.users
Salesperson = DFMBase.classes.salesperson_masters
Orders = getattr(DFMBase.classes, "orders_budget_2026", None)
