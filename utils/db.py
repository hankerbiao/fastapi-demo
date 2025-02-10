from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from models.News import NewNews

# 创建 SQLite 数据库和表
engine = create_engine("sqlite:///news.db")
SQLModel.metadata.create_all(engine)


def update_new_news(news_data: NewNews):
    with Session(engine) as session:
        try:
            # 首先尝试查找现有的记录
            existing_news = session.exec(
                select(NewNews).where(NewNews.url == news_data.url)
            ).first()

            if existing_news:
                # 如果记录存在，更新它
                existing_news.title = news_data.title
                existing_news.summary = news_data.summary
                existing_news.tags = news_data.tags
                existing_news.editor_time = news_data.editor_time
                existing_news.isFinanceOrEstate = news_data.isFinanceOrEstate
                # 可以根据需要更新其他字段
                session.commit()
                session.refresh(existing_news)
                return existing_news
            else:
                # 如果记录不存在，插入新记录
                session.add(news_data)
                session.commit()
                session.refresh(news_data)
                return news_data
        except Exception as e:
            session.rollback()
            return None


def check_url_exist(url):
    with Session(engine) as session:
        return True if session.exec(select(NewNews).where(NewNews.url == url)).first() else False


