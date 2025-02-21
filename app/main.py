from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes import user, stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Инициализация базы данных...")
    await init_db()
    yield  # Здесь FastAPI будет работать, пока сервер не завершится
    print("Завершение работы приложения")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


app.include_router(user.router, prefix="/auth", tags=["auth"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
