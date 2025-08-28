from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from agent import ghana_dev_news_team

app = FastAPI(
    title="TropiTrek Ghana Development News API",
    description="API for retrieving developmental news from Ghana for a specific place",
    version="1.0.0"
)

class PlaceRequest(BaseModel):
    place: str

class NewsResponse(BaseModel):
    news: str

@app.get("/")
async def root():
    return {"message": "Welcome to TropiTrek Ghana Development News API"}

@app.post("/news", response_model=NewsResponse)
async def get_news(request: PlaceRequest):
    if not request.place:
        raise HTTPException(status_code=400, detail="Place name is required")
    
    # Format the query for the agent
    query = f"Get me the recent developmental news for {request.place}"
    
    # Get response from the agent team
    # response = ghana_dev_news_team.print_response(
    #     query,
    #     stream=False,
    #     show_full_reasoning=False,
    #     stream_intermediate_steps=False,
    # )
    run_response = await ghana_dev_news_team.arun(query)
    response = run_response.content if hasattr(run_response, "content") else str(run_response)
    return NewsResponse(news=response)
    # return NewsResponse(news=response)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)