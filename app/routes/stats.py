from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import PageVisit
from app.schemas import PageVisitCreate, PageVisitFilter
from app.database import get_session

router = APIRouter()

@router.post("/log_visit")
async def log_visit(visit: PageVisitCreate, session: AsyncSession = Depends(get_session)):
    new_visit = PageVisit(page_url=visit.page_url)
    session.add(new_visit)
    await session.commit()
    return {"message": "Visit logged"}

@router.get("/statistics")
async def get_statistics(filters: PageVisitFilter, session: AsyncSession = Depends(get_session)):
    query = session.query(PageVisit)
    if filters.user_id:
        query = query.filter(PageVisit.user_id == filters.user_id)
    if filters.page_url:
        query = query.filter(PageVisit.page_url == filters.page_url)
    # Add date filters if provided
    results = await query.all()
    return results
