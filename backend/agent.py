
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat
from tools import TropicTrekToolkit
import asyncio
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.searxng import SearxngTools
import os
from dotenv import load_dotenv

load_dotenv()


# Initialize TropicTrek toolkit
tropictrek_toolkit = TropicTrekToolkit()
searxng = SearxngTools(
    host="https://search.disroot.org",
    engines=[],
    fixed_max_results=5,
    images=True,
)

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

agent = Agent(
    model=openrouter_model,
    tools=[tropictrek_toolkit, DuckDuckGoTools(), searxng],
    instructions=(
        "You are TropicTrek, a specialized tourism assistant for Eastern Caribbean Currency Union (ECCU) countries. "
        "Use DuckDuckGo search to find current information about ECCU destinations, attractions, and activities. "
        "When users want to see images of destinations, beaches, attractions, or places, use the search_destination_images tool to show beautiful photos from Unsplash. "
        "You can also try SearxNG for additional images if needed, but search_destination_images is your primary image tool. "
        "When users want a complete travel itinerary, use the create_itinerary_with_pdf tool to generate personalized itineraries with downloadable PDFs. "
        "Be enthusiastic about Caribbean culture and always ask for the traveler's name to personalize itineraries. "
        "Collect: traveler name, destination, travel style, trip duration, interests, and budget level for itinerary creation."
    ),
    system_message=(
        "You are TropicTrek, a helpful tourism agent specialized in ECCU countries travel planning. "
        "Available tools: "
        "- DuckDuckGo: Search for current information about destinations, attractions, restaurants, and activities "
        "- search_destination_images: Search for high-quality destination photos using Unsplash API (primary image tool) "
        "- SearxNG: Alternative image search (backup option) "
        "- create_itinerary_with_pdf: Generate detailed day-by-day travel plans with downloadable PDFs "
        ""
        "Tool usage strategy: "
        "1. For general information: Use DuckDuckGo search "
        "2. For images: Use search_destination_images as your primary tool for showing beautiful destination photos "
        "3. For complete itineraries: Use create_itinerary_with_pdf tool "
        ""
        "When users ask to see places, beaches, attractions, or want visual inspiration, proactively use search_destination_images. "
        "The ECCU countries are: Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, St. Vincent & the Grenadines. "
        ""
        "Always be enthusiastic about Caribbean culture and provide visual inspiration through beautiful destination photos."
    ),
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=3
)

async def main():
    """Main conversation loop for TropicTrek agent"""
    print("🌴 Welcome to TropicTrek! 🌴")
    print("Your AI assistant for Eastern Caribbean Currency Union travel planning!")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    # Initial greeting
    await agent.aprint_response(
        "Hello! I'm TropicTrek, your personal tourism assistant for the beautiful ECCU countries. "
        "I can help you plan personalized itineraries for destinations like St. Lucia, Grenada, Dominica, "
        "Antigua & Barbuda, St. Kitts & Nevis, and St. Vincent & the Grenadines. "
        "What kind of Caribbean adventure are you looking for?",
        stream=True,
        markdown=True
    )
    
    while True:
        user_input = input("\n🏝️ You: ")
        if user_input.lower() in {"exit", "quit", "bye", "goodbye"}:
            print("\n🌺 Thank you for using TropicTrek! Have an amazing Caribbean adventure! 🌺")
            break
            
        await agent.aprint_response(
            user_input, 
            stream=True, 
            markdown=True
        )

if __name__ == "__main__":
    asyncio.run(main())