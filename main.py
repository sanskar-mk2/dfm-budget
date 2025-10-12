from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.core import get_readonly_session

# from .db.budget_models import Budget, init_db
from db.dfm_reflect import Sales
from contextlib import asynccontextmanager
from controllers.auth_controller import router as auth_router
from controllers.sales_controller import router as sales_router
from controllers.budget_controller import router as budget_router
from middlewares.auth_middleware import AuthMiddleware
from constants import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(sales_router)
app.include_router(budget_router)
app.add_middleware(AuthMiddleware)
