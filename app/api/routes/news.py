from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, or_, func
from app.api.deps import SessionDep
from pydantic import BaseModel

from models.News import NewNews

router = APIRouter()

class PaginatedResponse(BaseModel):
    items: List[NewNews]
    total: int
    page: int
    pageSize: int

@router.get("/news", response_model=PaginatedResponse)
async def get_articles(
    db: SessionDep,
    startDate: Optional[datetime] = Query(None, description="开始时间"),
    endDate: Optional[datetime] = Query(None, description="结束时间"),
    isFinanceOrEstate: Optional[bool] = Query(None, description="是否为金融/地产相关"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页条数")
):
    try:
        query = select(NewNews)

        if startDate:
            startDate = startDate.replace(tzinfo=timezone.utc)
            query = query.where(NewNews.editor_time >= startDate)
        if endDate:
            endDate = endDate.replace(tzinfo=timezone.utc)
            query = query.where(NewNews.editor_time <= endDate)
        if isFinanceOrEstate:
            query = query.where(NewNews.isFinanceOrEstate == 1)

        if keyword:
            keyword = keyword.strip()
            query = query.where(
                or_(
                    NewNews.title.icontains(keyword),
                    NewNews.summary.icontains(keyword),
                    NewNews.tags.icontains(keyword)
                )
            )

        # 计算总数
        total_query = select(func.count()).select_from(query.subquery())
        total = db.exec(total_query).one()

        # 添加排序
        query = query.order_by(NewNews.editor_time.desc())

        # 添加分页
        offset = (page - 1) * pageSize
        query = query.offset(offset).limit(pageSize)

        articles = db.exec(query).all()

        return PaginatedResponse(
            items=articles,
            total=total,
            page=page,
            pageSize=pageSize
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")