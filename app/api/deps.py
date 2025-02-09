from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

engine = create_engine(r"sqlite:///news.db")

SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
