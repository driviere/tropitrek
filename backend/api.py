from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import asyncio
import uuid
from datetime import datetime
import logging

# Import our TropicTrek components
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat
from agno.tools.searxng import SearxngTools
from tools import TropicTrekToolkit
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TropicTrek API",
    description="AI Tourism Assistant for ECCU Countries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TropicTrek components
tropictrek_toolkit = TropicTrekToolkit()


# Create OpenRouter model
openrouter_model = OpenAIChat(
    id="google/gemini-2.5-flash",
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
    extra_headers={
        "HTTP-Referer": os.getenv('SITE_URL', 'https://tropictrek.com'),
        "X-Title": os.getenv('SITE_NAME', 'TropicTrek'),
    }
)

# Initialize agent
agent = Agent(
    model=openrouter_model,
    tools=[tropictrek_toolkit, DuckDuckGoTools()],
    instructions=(
        "You are TropicTrek, a specialized tourism assistant for Eastern Caribbean Currency Union (ECCU) countries. "
        "Use DuckDuckGo search to find current information about ECCU destinations, attractions, and activities. "
        "When users want to see images of destinations, beaches, attractions, or places, use the search_destination_images tool to show beautiful photos from Unsplash. "
        "When users want a complete travel itinerary, use the create_itinerary_with_pdf tool to generate personalized itineraries with downloadable PDFs. "
        "Be enthusiastic about Caribbean culture and always ask for the traveler's name to personalize itineraries. "
        "Collect: traveler name, destination, travel style, trip duration, interests, and budget level for itinerary creation."
    ),
    system_message=(
        "You are TropicTrek, a helpful tourism agent specialized in ECCU countries travel planning. "
        "Available tools: "
        "- DuckDuckGo: Search for current information about destinations, attractions, restaurants, and activities "
        "- search_destination_images: Search for high-quality destination photos using Unsplash API (primary image tool) "
        "- create_itinerary_with_pdf: Generate detailed day-by-day travel plans with downloadable PDFs "
        ""
        "Tool usage strategy: "
        "1. For general information: Use DuckDuckGo search "
        "2. For images: Use search_destination_images as your primary tool for showing beautiful destination photos "
        "3. For complete itineraries: Use create_itinerary_with_pdf tool "
        "The ECCU countries are: Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, St. Vincent & the Grenadines. "
        ""
        "Always be enthusiastic about Caribbean culture and provide engaging descriptions even without images."
    ),
    markdown=True,
    add_history_to_messages=True,
    show_tool_calls=False,  # Disable for API responses
    debug_mode=False,       # Disable for production
)

# Store active sessions and generated PDFs
sessions: Dict[str, Dict[str, Any]] = {}
generated_pdfs: Dict[str, str] = {}  # Maps PDF ID to file path

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    pdf_generated: bool = False
    pdf_id: Optional[str] = None

# Removed ItineraryRequest and ItineraryResponse - not needed since agent handles everything

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TropicTrek API",
        "description": "AI Tourism Assistant for ECCU Countries",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "download_pdf": "/download/{pdf_id}"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for conversational interaction with TropicTrek agent
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.now(),
                "messages": []
            }
        
        # Add user message to session
        sessions[session_id]["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now()
        })
        
        logger.info(f"Processing chat request for session {session_id}")
        
        # Get response from agent
        run_response = await agent.arun(request.message)
        
        # Extract the actual response content
        response = run_response.content if hasattr(run_response, 'content') else str(run_response)
        
        # Add agent response to session
        sessions[session_id]["messages"].append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now()
        })
        
        # Check if a PDF was generated (look for PDF filename in response)
        pdf_generated = False
        pdf_id = None
        
        if "TropicTrek_Itinerary_" in response and ".pdf" in response:
            # Extract PDF filename from response
            lines = response.split('\n')
            for line in lines:
                if "PDF Generated:" in line and ".pdf" in line:
                    # Extract filename between backticks
                    start = line.find('`') + 1
                    end = line.rfind('`')
                    if start > 0 and end > start:
                        pdf_filename = line[start:end]
                        if os.path.exists(pdf_filename):
                            pdf_id = str(uuid.uuid4())
                            generated_pdfs[pdf_id] = pdf_filename
                            pdf_generated = True
                            logger.info(f"PDF generated and registered: {pdf_id} -> {pdf_filename}")
                            break
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            pdf_generated=pdf_generated,
            pdf_id=pdf_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/download/{pdf_id}")
async def download_pdf(pdf_id: str):
    """
    Download endpoint for generated PDF files
    """
    try:
        if pdf_id not in generated_pdfs:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        pdf_path = generated_pdfs[pdf_id]
        
        if not os.path.exists(pdf_path):
            # Clean up invalid reference
            del generated_pdfs[pdf_id]
            raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
        logger.info(f"Serving PDF download: {pdf_id} -> {pdf_path}")
        
        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF {pdf_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download PDF")

@app.get("/pdfs")
async def list_pdfs():
    """
    List all available PDFs (for debugging/admin purposes)
    """
    return {
        "available_pdfs": {
            pdf_id: {
                "filename": os.path.basename(path),
                "exists": os.path.exists(path),
                "size": os.path.getsize(path) if os.path.exists(path) else 0
            }
            for pdf_id, path in generated_pdfs.items()
        }
    }

@app.delete("/cleanup")
async def cleanup_old_files():
    """
    Cleanup old PDF files and sessions (admin endpoint)
    """
    try:
        cleaned_pdfs = 0
        cleaned_sessions = 0
        
        # Clean up PDFs older than 24 hours
        current_time = datetime.now()
        for pdf_id, pdf_path in list(generated_pdfs.items()):
            try:
                if os.path.exists(pdf_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(pdf_path))
                    if (current_time - file_time).total_seconds() > 86400:  # 24 hours
                        os.remove(pdf_path)
                        del generated_pdfs[pdf_id]
                        cleaned_pdfs += 1
                else:
                    del generated_pdfs[pdf_id]
                    cleaned_pdfs += 1
            except Exception as e:
                logger.error(f"Error cleaning PDF {pdf_id}: {e}")
        
        # Clean up old sessions
        for session_id, session_data in list(sessions.items()):
            if (current_time - session_data["created_at"]).total_seconds() > 86400:  # 24 hours
                del sessions[session_id]
                cleaned_sessions += 1
        
        return {
            "message": "Cleanup completed",
            "cleaned_pdfs": cleaned_pdfs,
            "cleaned_sessions": cleaned_sessions
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_sessions": len(sessions),
        "available_pdfs": len(generated_pdfs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)