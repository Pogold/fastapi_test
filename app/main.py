from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from app.core.database import engine, drop_all_tables, create_tables
from app.routers import users_routes, stats_routes

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    #await drop_all_tables()
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(
    title="Analytics API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.include_router(users_routes.router)
app.include_router(stats_routes.router)
