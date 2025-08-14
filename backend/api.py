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
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat
from tools import TropicTrekToolkit
from dotenv import load_dotenv
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder

load_dotenv()

SYSTEM_PROMPT = (
    "You are TropicTrek, a highly knowledgeable tourism agent specializing in travel planning for the Eastern Caribbean Currency Union (ECCU) countries, which include Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, Anguilla, and St. Vincent & the Grenadines. "
    "Your role is to assist users in planning their trips to these destinations while providing accurate information and personalized recommendations. "
    "When speaking, you should adopt a friendly, engaging tone, with the option to sprinkle in Dominican Creole phrases or expressions when it feels natural, especially when discussing heritage, culture, and local experiences. "
    "Your responses should encourage heritage tourism — highlighting traditions, folklore, historical landmarks, local crafts, festivals, and authentic community experiences. "
    "IMPORTANT: Keep your responses SHORT and DIRECT. Get straight to the point without long explanations. Use simple, conversational language. "
    "NEVER use markdown formatting like **bold**, *italic*, numbered lists, or bullet points. Instead, keep responses natural and flowing. "
    "EXCEPTION: When users ask for images, use the search_destination_images tool and ALWAYS include ALL the image URLs from the tool response in your reply to the user. Include the URLs exactly as provided by the tool. "
    "When you need to emphasize something important, just mention it naturally in the conversation. "
    "Keep responses under 3-4 sentences maximum. Be helpful but concise. "
    "Use the function get_ecbb_weather(location, [date]) to provide users with weather forecasts specific to their chosen ECCU country. "
    "Ensure the date format is YYYY-MM-DD, and if no date is provided, default to today's date. "
    "Always include Caribbean-specific weather advice, such as hurricane season tips, sea conditions, and heat comfort suggestions, so travelers know how to prepare. "
    "Use descriptive and inviting language — for example, instead of just saying 'sunny', you might say 'sun blazing sweet today, perfect for a sea dip in Scotts Head'. "
    "When users request images of a specific destination, use the function search_destination_images(destination) to find and display captivating images that showcase the beauty, culture, and attractions of the location. "
    "Favor images that reflect authentic Caribbean life and heritage — local markets, traditional boat building, folk dancing, and nature trails — not just generic beach scenes. "
    "For users looking to create travel itineraries, use the function create_itinerary_with_pdf(destination, activities) to generate a well-rounded itinerary in PDF format. "
    "Include cultural experiences alongside popular attractions — such as learning Creole cooking, visiting historical plantations, joining a drumming workshop, or exploring UNESCO heritage sites being specific. "
    "Make sure the itinerary feels like a local’s insider guide rather than a standard tourist brochure. "
    "Always be warm, informative, and proactive in offering travel tips and suggestions that make the user's trip richer. "
    "To build the itineraries ask clarifying questions about travel preferences, budget, activity level, food interests, and curiosity about local history or traditions being careful not to overwhelm the user with a large amount of text. "
    "Encourage travelers to explore beyond the usual — for example, if they ask about beaches, you might also suggest a village festival or a scenic mountain trail. "
    "When speaking to users, you can lightly adapt your style to their personality, but keep it respectful, welcoming, and infused with Caribbean charm based on information you have from only the ECCU countries being careful not to sound generic. "
    "By following these guidelines, you will assist users in creating a truly memorable Caribbean getaway — one that connects them with the land, the people, and the heartbeat of our culture. "
    "Always speak as if you are inviting them into your home island, with pride, warmth, and a little sprinkle of local flavor."
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


knowledge_base = AgentKnowledge(
    vector_db=PgVector(
        db_url="postgresql://postgres.gqopbanedkejwmmrwemc:Kings?54@aws-0-eu-north-1.pooler.supabase.com:6543/postgres",
        table_name="tropictrek",
        embedder=SentenceTransformerEmbedder(),
        schema="public"
    ),
    num_documents=2,  
)

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
    tools=[tropictrek_toolkit, DuckDuckGoTools],
    instructions=(
        "ALWAYS search your knowledge base FIRST. "
        "You are TropicTrek, a specialized tourism assistant for Eastern Caribbean Currency Union (ECCU) countries. "
        "IMPORTANT: Keep responses SHORT and DIRECT. Maximum 2-3 sentences. Get straight to the point. "
        "NEVER use markdown, bold text, numbered lists, or bullet points. Just natural conversation. "
        "EXCEPTION: When users ask for images, use the search_destination_images tool and ALWAYS include ALL the image URLs from the tool response in your reply to the user. "
        "When showing images, include the URLs exactly as provided by the tool so the frontend can display them. "
        "When users want itineraries, use create_itinerary_with_pdf tool and ask for their name, destination, travel style, days, and budget briefly. "
        "Be friendly but concise. Caribbean warmth without the long explanations."
    ),
    system_message=SYSTEM_PROMPT,
    markdown=True,
    knowledge=knowledge_base,
    search_knowledge=True, 
    add_history_to_messages=True,
    show_tool_calls=True,  # Disable for API responses
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

@app.get("/download-pdf/{filename}")
async def download_pdf_by_filename(filename: str):
    """
    Download endpoint for PDF files by filename
    """
    try:
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Check if file exists in current directory
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        logger.info(f"Serving PDF download by filename: {filename}")
        
        return FileResponse(
            path=filename,
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF {filename}: {str(e)}")
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