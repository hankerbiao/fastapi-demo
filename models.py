from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class NewNews(SQLModel, table=True):
    __tablename__ = "newnews"
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(sa_column_kwargs={"unique": True})  # 唯一
    title: Optional[str] = Field(default=None)
    tags: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    isFinanceOrEstate: Optional[bool] = Field(default=False)
    editor_time: Optional[datetime] = Field(default=None)
