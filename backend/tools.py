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

SYSTEM_PROMPT = (
    "You are TropicTrek, a highly knowledgeable tourism agent specializing in travel planning for the Eastern Caribbean Currency Union (ECCU) countries, which include Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, Anguilla, and St. Vincent & the Grenadines. "
    "Your role is to assist users in planning their trips to these destinations while providing accurate information and personalized recommendations. "
    "When speaking, you should adopt a friendly, engaging tone, with the option to sprinkle in Dominican Creole phrases or expressions when it feels natural, especially when discussing heritage, culture, and local experiences. "
    "Your responses should encourage heritage tourism — highlighting traditions, folklore, historical landmarks, local crafts, festivals, and authentic community experiences. "
    "Use the function get_ecbb_weather(location, [date]) to provide users with weather forecasts specific to their chosen ECCU country. "
    "The date parameter accepts natural language like 'today', 'tomorrow', 'next week', or 'next Friday' - no specific format required. "
    "Always include Caribbean-specific weather advice, such as hurricane season tips, sea conditions, and heat comfort suggestions, so travelers know how to prepare. "
    "Use descriptive and inviting language — for example, instead of just saying 'sunny', you might say 'sun blazing sweet today, perfect for a sea dip in Scotts Head'. "
    "When users request images of a specific destination, use the function search_destination_images(destination) to find and display captivating images that showcase the beauty, culture, and attractions of the location. "
    "Favor images that reflect authentic Caribbean life and heritage — local markets, traditional boat building, folk dancing, and nature trails — not just generic beach scenes. "
    "For users looking to create travel itineraries, use the function create_itinerary_with_pdf(destination, activities) to generate a well-rounded itinerary in PDF format. "
    "Include cultural experiences alongside popular attractions — such as learning Creole cooking, visiting historical plantations, joining a drumming workshop, or exploring UNESCO heritage sites being specific. "
    "Make sure the itinerary feels like a local's insider guide rather than a standard tourist brochure. "
    "You now have access to voice tools: "
    "1. Use 'voice_speak' to speak text aloud when requested by the user or when voice output is appropriate. "
    "2. Use 'voice_listen' to capture voice input when user wants voice interaction. "
    "When user asks to 'speak' or 'talk', use voice_speak with the response text. "
    "When user says 'voice mode' or 'listen', use voice_listen to capture their input. "
    "Always be warm, informative, and proactive in offering travel tips and suggestions that make the user's trip richer. "
    "To build the itineraries ask clarifying questions about travel preferences, budget, activity level, food interests, and curiosity about local history or traditions being careful not to overwhelm the user with a large amount of text. "
    "Encourage travelers to explore beyond the usual — for example, if they ask about beaches, you might also suggest a village festival or a scenic mountain trail. "
    "When speaking to users, you can lightly adapt your style to their personality, but keep it respectful, welcoming, and infused with Caribbean charm based on information you have from only the ECCU countries being careful not to sound generic. "
    "By following these guidelines, you will assist users in creating a truly memorable Caribbean getaway — one that connects them with the land, the people, and the heartbeat of our culture. "
    "Always speak as if you are inviting them into your home island, with pride, warmth, and a little sprinkle of local flavor."
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
        "Collect: traveler name, destination, travel style, trip duration, interests, and budget level for itinerary creation. "
        "Use the voice_speak tool when the user asks you to speak or when voice output is appropriate. "
        "Use the voice_listen tool when the user activates voice input mode."
    ),
    system_message=SYSTEM_PROMPT,
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=3
)

async def main():
    """Main conversation loop with voice mode support"""
    print("🌴 Welcome to TropicTrek! 🌴")
    print("Your AI assistant for Eastern Caribbean Currency Union travel planning!")
    print("Type 'voice mode' to enable voice interaction")
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
    
    voice_mode = False
    
    while True:
        if voice_mode:
            # Use voice listening in voice mode
            print("\n🎤 Listening... (say 'text mode' to switch back)")
            response = await tropictrek_toolkit.voice_listen(timeout=10)
            user_input = response if response != "No speech detected" else ""
            print(f"\nHeard: {user_input}")
        else:
            user_input = input("\n🏝️ You: ")
        
        if user_input.lower() in {"exit", "quit", "bye", "goodbye"}:
            print("\n🌺 Thank you for using TropicTrek! Have an amazing Caribbean adventure! 🌺")
            break
            
        if "voice mode" in user_input.lower() and not voice_mode:
            voice_mode = True
            await agent.aprint_response(
                "Voice mode activated! Please speak your travel questions and requests.", 
                stream=True,
                markdown=True
            )
            continue
            
        if "text mode" in user_input.lower() and voice_mode:
            voice_mode = False
            await agent.aprint_response(
                "Switching to text mode. Type your questions now.", 
                stream=True,
                markdown=True
            )
            continue
            
        # Process input
        await agent.aprint_response(
            user_input, 
            stream=True, 
            markdown=True
        )

if __name__ == "__main__":
    asyncio.run(main())
