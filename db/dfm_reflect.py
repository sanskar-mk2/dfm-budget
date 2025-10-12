from sqlalchemy.ext.automap import automap_base
from .core import engine

DFMBase = automap_base()
DFMBase.prepare(autoload_with=engine)

Sales = DFMBase.classes.sales
Users = DFMBase.classes.users
Salesperson = DFMBase.classes.salesperson_masters
Orders = DFMBase.classes.open_orders
