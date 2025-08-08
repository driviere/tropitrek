import asyncio
import requests
import os
import re
from datetime import datetime
from dotenv import load_dotenv

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.searxng import SearxngTools
from agno.models.openai import OpenAIChat

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or "c4ef22d598ec91e8a1f03a0c18718cf4"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"

class TropicTrekToolkit:
    def get_ecbb_weather(self, location: str, target_date: str = None) -> dict:
        eccb_islands = {
            "anguilla": "AI", "antigua": "AG", "dominica": "DM",
            "grenada": "GD", "montserrat": "MS", "st kitts": "KN",
            "nevis": "KN", "saint lucia": "LC", "st vincent": "VC"
        }
        loc_key = location.lower().strip()
        if loc_key not in eccb_islands:
            return {
                "error": "Only ECCB islands supported: Anguilla, Antigua, Dominica, Grenada, Montserrat, St. Kitts, Nevis, Saint Lucia, St. Vincent"
            }
        today = datetime.now().date()
        if target_date:
            try:
                target = datetime.strptime(target_date, "%Y-%m-%d").date()
                day_diff = (target - today).days
                if day_diff < 0:
                    return {"error": "Date cannot be in the past"}
                if day_diff > 10:
                    return {"error": "Weather forecasts beyond 10 days are unavailable"}
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
        else:
            target = today
            day_diff = 0
        try:
            country_code = eccb_islands[loc_key]
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location},{country_code}&limit=1&appid={OPENWEATHER_API_KEY}"
            geo_res = requests.get(geo_url)
            if geo_res.status_code != 200:
                return {"error": "Failed to fetch location data"}
            geo_data = geo_res.json()
            if not geo_data:
                return {"error": "Location not found"}
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

            if day_diff == 0:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                if response.status_code != 200:
                    return {"error": "Failed to fetch current weather data"}
                data = response.json()
                weather_id = data['weather'][0]['id']
                weather_main = data['weather'][0]['main']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description']
            else:
                url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                if response.status_code != 200:
                    return {"error": "Failed to fetch weather forecast data"}
                data = response.json()
                target_dates = [
                    item for item in data['list']
                    if datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S").date() == target
                ]
                if not target_dates:
                    return {"error": "Forecast not available for selected date"}
                mid_index = len(target_dates) // 2
                weather_id = target_dates[mid_index]['weather'][0]['id']
                weather_main = target_dates[mid_index]['weather'][0]['main']
                temp = target_dates[mid_index]['main']['temp']
                humidity = target_dates[mid_index]['main']['humidity']
                description = target_dates[mid_index]['weather'][0]['description']

            # Add more nuanced weather descriptions with emojis
            if 200 <= weather_id < 300:
                special = "⚡ Thunderstorms brewing! Best time for some indoor rum tasting 🍹."
            elif 300 <= weather_id < 500:
                special = "🌧️ Light showers - perfect for a cozy rainforest bath and spice tours 🌿."
            elif 500 <= weather_id < 600:
                special = "☔ Rainy vibes — great day for museums or cooking classes 🍲."
            elif 600 <= weather_id < 700:
                special = "❄️ Cool breezes — ideal for cafes and cultural visits ☕️."
            elif 700 <= weather_id < 800:
                special = "🌫️ Misty magic — bring your camera for stunning scenic shots 📸."
            elif weather_id == 800:
                special = "☀️ Sun blazing sweet today — perfect for a sea dip and beach limin' 🏖️."
            else:
                special = "☁️ Partly cloudy — nice for hikes without the full Caribbean heat 🥾."

            # Combine descriptive text with the weather description (adding emojis)
            text_summary = (
                f"Weather in {location.title()} on {target.strftime('%Y-%m-%d')}:\n"
                f"{description.capitalize()} 🌤️\n"
                f"Temperature: {temp}°C 🌡️\n"
                f"Humidity: {humidity}% 💧\n"
                f"{special}"
            )

            return {
                "location": location.title(),
                "date": target.strftime('%Y-%m-%d'),
                "weather": weather_main,
                "temperature": temp,
                "humidity": humidity,
                "special_response": special,
                "text_summary": text_summary
            }
        except Exception as e:
            return {"error": f"Weather fetch failed: {str(e)}"}

    def search_destination_images(self, query: str):
        # Example stub returning placeholder images
        return [{"url": f"https://example.com/{query.replace(' ', '_')}.jpg"}]

    def create_itinerary_with_pdf(self, details: dict):
        # Stub function — replace with actual PDF creation logic if needed
        return {"itinerary": "Sample itinerary", "pdf_url": "https://example.com/itinerary.pdf"}


duckduckgo = DuckDuckGoTools()
searxng = SearxngTools(
    host="https://search.disroot.org",
    engines=[],
    fixed_max_results=5,
    images=True
)
tropictrek_toolkit = TropicTrekToolkit()

openrouter_model = OpenAIChat(
    id="openai/gpt-oss-120b",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    extra_headers={
        "HTTP-Referer": os.getenv('SITE_URL', 'https://tropictrek.com'),
        "X-Title": os.getenv('SITE_NAME', 'TropicTrek')
    }
)

SYSTEM_PROMPT = (
    "You are TropicTrek, a highly knowledgeable tourism agent specializing in travel planning for the Eastern Caribbean Currency Union (ECCU) countries, which include Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, Anguilla, and St. Vincent & the Grenadines. "
    "Your role is to assist users in planning their trips to these destinations while providing accurate information and personalized recommendations. "
    "When speaking, you should adopt a friendly, engaging tone, with the option to sprinkle in Dominican Creole phrases or expressions when it feels natural, especially when discussing heritage, culture, and local experiences. "
    "Your responses should encourage heritage tourism — highlighting traditions, folklore, historical landmarks, local crafts, festivals, and authentic community experiences. "
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

agent = Agent(
    system_message=SYSTEM_PROMPT,
    tools=[tropictrek_toolkit, duckduckgo, searxng],
    model=openrouter_model,
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,
    enable_agentic_memory=True,
    add_history_to_messages=True,
    num_history_runs=3,
    verbose=True
)


async def main():
    print("🌴 What's the word my friend, I'is TropicTrek! 🌴")
    print("I gan be your AI assistant for ECCU travel planning! 🌞")
    print("Before we start, what’s your name? 🤗\n")

    user_name = input("🏝️ You: ").strip()
    if not user_name:
        user_name = "friend"

    await agent.aprint_response(
        f"Sa ca fete, {user_name}! I'm TropicTrek, your personal tourism assistant for the ECCU countries.\n"
        "I'll help you with weather forecasts, itinerary planning, and destination recommendations for islands like:\n"
        "- St. Lucia\n- Grenada\n- Dominica\n- Antigua & Barbuda\n- St. Kitts & Nevis\n- Anguilla\n- St. Vincent & the Grenadines\n\n"
        "What kin'a Caribbean experience you looking for, {user_name}?",
        stream=True,
        markdown=False  
    )

    while True:
        user_input = input(f"\n🏝️ {user_name}: ").strip()
        if user_input.lower() in {"exit", "quit", "bye", "goodbye", "later"}:
            print(f"\n🌺 Thanks for using TropicTrek, {user_name}! Have an amazing Caribbean adventure! 🌺")
            break

        # Detect weather requests more flexibly
        if "weather" in user_input.lower():
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", user_input)
            date = date_match.group(0) if date_match else None
            possible_locations = [
                "anguilla", "antigua", "dominica", "grenada", "montserrat",
                "st kitts", "nevis", "saint lucia", "st vincent"
            ]
            location = next((loc for loc in possible_locations if loc in user_input.lower()), None)
            if location:
                weather_info = tropictrek_toolkit.get_ecbb_weather(location, date)
                if "error" in weather_info:
                    print(f"TropicTrek 🤖: Sorry, {weather_info['error']}")
                else:
                    print(f"TropicTrek 🤖: {weather_info['text_summary']}")
            else:
                print("TropicTrek 🤖: Lemme know for which island you want the weather info, please.")
        else:
            await agent.aprint_response(
                user_input,
                stream=True,
                markdown=False  
            )


if __name__ == "__main__":
    asyncio.run(main())
