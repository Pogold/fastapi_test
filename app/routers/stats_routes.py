from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from starlette import status
from app.core.security import get_current_user
from app.core.database import get_db
from app.crud.stats import create_visit, get_visits, get_unique_users_count, get_popular_pages, get_visit_count
from app.crud.user import get_user_by_email
from app.schemas.stats_schema import VisitCreate, StatisticsResponse

router = APIRouter(tags=["Statistics"])


# Трекинг посещения страницы
@router.post("/visits", status_code=status.HTTP_201_CREATED)
async def track_visit(
        visit_data: VisitCreate,
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    visit = await create_visit(db, visit_data, user.id)
    return {"message": "Visit tracked successfully", "visit_id": visit.id}


# Получение статистики посещений
@router.get("/statistics", response_model=list[StatisticsResponse])
async def get_statistics(
        user_id: Optional[int] = Query(None),
        page_url: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    visits = await get_visits(db, user_id, page_url, start_date, end_date)
    return visits


# Получение сводной статистики
@router.get("/statistics/summary")
async def get_summary_statistics(
        db: AsyncSession = Depends(get_db)
):
    total_visits = await get_visit_count(db)
    unique_users = await get_unique_users_count(db)
    popular_pages = await get_popular_pages(db)

    return {
        "total_visits": total_visits,
        "unique_users": unique_users,
        "popular_pages": popular_pages
    }
