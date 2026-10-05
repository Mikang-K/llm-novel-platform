from fastapi import FastAPI
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

@app.post("/novels")
def create_novel(data: NovelCreate):
    return {
        "id": 1, 
        "title": data.title, 
        "description": data.description
        }
