from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class NovelCreate(BaseModel):
    title: str
    description: str

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
