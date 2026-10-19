from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Novel

app = FastAPI()

Base.metadata.create_all(bind=engine)

DbSession = Annotated[Session, Depends(get_db)]

class NovelCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def title_validator(cls, value):
        if isinstance(value,str):
            return value.strip()
        return value 

class NovelResponse(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = {"from_attributes": True}

@app.get("/health")
def get_status():
    return {"status": "ok"}

@app.post("/novels", response_model=NovelResponse, status_code=201)
def create_novel(data: NovelCreate, db: DbSession):
    novel = Novel(
        title=data.title,
        description=data.description
    )

    db.add(novel)
    db.commit()
    db.refresh(novel)

    return novel

@app.get("/novels/{novel_id}", response_model=NovelResponse)
def get_novel(novel_id: int, db:DbSession):
    novel = db.get(Novel, novel_id)

    if novel is None:
        raise HTTPException(
            status_code=404,
            detail="Novel not Found"
        )
    return novel