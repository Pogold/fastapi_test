from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from app.models.stats_model import PageVisit
from app.schemas.stats_schema import VisitCreate, StatisticsResponse


async def create_visit(db: AsyncSession, visit_data: VisitCreate, user_id: Optional[int]) -> PageVisit:
    """
    Создание записи о посещении страницы
    """
    visit = PageVisit(
        user_id=user_id,
        page_url=visit_data.page_url,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return visit


async def get_visits(
        db: AsyncSession,
        user_id: Optional[int] = None,
        page_url: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> list[StatisticsResponse]:
    """
    Получение отфильтрованного списка посещений с пагинацией
    """
    query = select(PageVisit)

    if user_id:
        query = query.where(PageVisit.user_id == user_id)
    if page_url:
        query = query.where(PageVisit.page_url == page_url)
    if start_date:
        query = query.where(PageVisit.timestamp >= start_date)
    if end_date:
        query = query.where(PageVisit.timestamp <= end_date)

    result = await db.execute(query)
    visits = result.scalars().all()
    return [StatisticsResponse(
        id=visit.id,
        user_id=visit.user_id,
        page_url=visit.page_url,
        timestamp=visit.timestamp
    ) for visit in visits]


async def get_visit_count(
        db: AsyncSession,
        user_id: Optional[int] = None,
        page_url: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> int:
    """
    Получение общего количества посещений по фильтрам
    """
    query = select(func.count(PageVisit.id))

    if user_id:
        query = query.where(PageVisit.user_id == user_id)
    if page_url:
        query = query.where(PageVisit.page_url == page_url)
    if start_date:
        query = query.where(PageVisit.timestamp >= start_date)
    if end_date:
        query = query.where(PageVisit.timestamp <= end_date)

    result = await db.scalar(query)
    return result or 0


async def get_unique_users_count(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> int:
    """
    Получение количества уникальных пользователей
    """
    query = select(func.count(distinct(PageVisit.user_id)))

    if start_date:
        query = query.where(PageVisit.timestamp >= start_date)
    if end_date:
        query = query.where(PageVisit.timestamp <= end_date)

    return await db.scalar(query) or 0


async def get_popular_pages(
        db: AsyncSession,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> list[dict]:
    """
    Получение списка популярных страниц
    """
    query = (
        select(
            PageVisit.page_url,
            func.count(PageVisit.id).label("visits"),
            func.count(distinct(PageVisit.user_id)).label("unique_users")
        )
        .group_by(PageVisit.page_url)
        .order_by(func.count(PageVisit.id).desc())
        .limit(limit)
    )

    if start_date:
        query = query.where(PageVisit.timestamp >= start_date)
    if end_date:
        query = query.where(PageVisit.timestamp <= end_date)

    result = await db.execute(query)
    return [{
        "page_url": row.page_url,
        "visits": row.visits,
        "unique_users": row.unique_users
    } for row in result.all()]


async def get_user_activity(
        db: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> dict:
    """
    Получение статистики активности конкретного пользователя
    """
    base_query = select(PageVisit).where(PageVisit.user_id == user_id)

    if start_date:
        base_query = base_query.where(PageVisit.timestamp >= start_date)
    if end_date:
        base_query = base_query.where(PageVisit.timestamp <= end_date)

    # Общее количество посещений
    total_visits = await db.scalar(
        select(func.count(PageVisit.id)).select_from(base_query)
    )

    # Популярные страницы пользователя
    popular_pages = await db.execute(
        select(
            PageVisit.page_url,
            func.count(PageVisit.id).label("visits")
        )
        .select_from(base_query)
        .group_by(PageVisit.page_url)
        .order_by(func.count(PageVisit.id).desc())
        .limit(5)
    )

    return {
        "total_visits": total_visits or 0,
        "popular_pages": [
            {"page_url": row.page_url, "visits": row.visits}
            for row in popular_pages.all()
        ]
    }