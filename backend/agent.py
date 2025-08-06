import asyncio
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.searxng import SearxngTools
from tools import TropicTrekToolkit
from agno.models.openai import OpenAIChat

load_dotenv()

OPENWEATHER_API_KEY = "c4ef22d598ec91e8a1f03a0c18718cf4"
OPENROUTER_API_KEY = "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"

# Initialize tools
duckduckgo = DuckDuckGoTools()
searxng = SearxngTools(
    host="https://search.disroot.org",
    engines=[],
    fixed_max_results=5,
    images=True
)
tropictrek_toolkit = TropicTrekToolkit()

# Define AI model
openrouter_model = OpenAIChat(
    id="google/gemini-2.5-flash",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    extra_headers={
        "HTTP-Referer": os.getenv('SITE_URL', 'https://tropictrek.com'),
        "X-Title": os.getenv('SITE_NAME', 'TropicTrek')
    }
)

# Create agent
agent = Agent(
    model=openrouter_model,
    tools=[tropictrek_toolkit, duckduckgo, searxng],
    instructions=(
        "You are TropicTrek, a specialized tourism assistant for Eastern Caribbean Currency Union (ECCU) countries. "
        "Use DuckDuckGo search to find current information about ECCU destinations, attractions, and activities. "
        "When users want to see images of destinations, beaches, attractions, or places, use the search_destination_images tool to show beautiful photos from Unsplash. "
        "You can also try SearxNG for additional images if needed. "
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
        "\nTool usage strategy: "
        "1. For general information: Use DuckDuckGo search "
        "2. For images: Use search_destination_images as your primary tool for showing beautiful destination photos "
        "3. For complete itineraries: Use create_itinerary_with_pdf tool "
        "\nWhen users ask to see places, beaches, attractions, or want visual inspiration, proactively use search_destination_images. "
        "The ECCU countries are: Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, St. Vincent & the Grenadines. "
        "\nAlways be enthusiastic about Caribbean culture and provide visual inspiration through beautiful destination photos."
    ),
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=3
)

async def main():
    print("🌴 Wago I'is TropicTrek! 🌴")
    print("I gan be your AI assistant for ECCU travel planning!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    await agent.aprint_response(
        "Sa ca fete ! I'm TropicTrek, your personal tourism assistant for the ECCU countries.\n"
        "I gan help you plan personalized itineraries for islands like St. Lucia, Grenada, Dominica,\n"
        "Antigua & Barbuda, St. Kitts & Nevis, and St. Vincent & the Grenadines.\n"
        "What kin'a Caribbean trip you looking for?",
        stream=True,
        markdown=True
    )

    while True:
        user_input = input("\n🏝️ You: ")
        if user_input.lower() in {"exit", "quit", "bye", "goodbye", "later"}:
            print("\n🌺 Thank you for using TropicTrek! Have an amazing Caribbean adventure! 🌺")
            break

        await agent.aprint_response(
            user_input,
            stream=True,
            markdown=True
        )

if __name__ == "__main__":
    asyncio.run(main())
