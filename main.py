from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.core import get_readonly_session

# from .db.budget_models import Budget, init_db
from db.dfm_reflect import Sales
from contextlib import asynccontextmanager
from controllers.auth_controller import router
from middlewares.auth_middleware import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.add_middleware(AuthMiddleware)


@app.get("/sales")
def list_sales(db=Depends(get_readonly_session)):
    return db.query(Sales).limit(10).all()
