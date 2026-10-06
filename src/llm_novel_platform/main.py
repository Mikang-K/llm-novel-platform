from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

class NovelCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def title_validator(cls, value: str):
        value = value.strip()
        if isinstance(value,str):
            return value.strip()
        return value 

@app.get("/health")
def get_status():
    return {"status": "ok"}

novels = {}
next_id = 1

@app.post("/novels")
def create_novel(data: NovelCreate):
    global next_id

    novel_id = next_id
    novels[novel_id] = {
        "id":novel_id,
        "title":data.title, 
        "description":data.description
    }
    next_id += 1

    return novels[novel_id]

@app.get("/novels/{novel_id}")
def get_novel(novel_id: int):
    if novel_id not in novels:
        raise HTTPException(
            status_code=404,
            detail="Novel not Found"
        )
    return novels[novel_id]