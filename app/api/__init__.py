from fastapi import APIRouter
from app.api.routes import news

api_route = APIRouter()
api_route.include_router(news.router, tags=["新闻列表"])
