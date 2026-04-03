from fastapi import FastAPI
from pydantic import BaseModel
from matcher import match

app = FastAPI()

class MatchRequest(BaseModel):
    skills: str
    job_description: str
    threshold: float = 60.0

@app.post("/get_score")
async def get_match_score(data: MatchRequest):
    score = match(data.skills, data.job_description, data.threshold)
    return {"match_score": score}