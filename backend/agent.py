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
            if 200 <= weather_id < 300:
                special = "⚡ Thunderstorms brewing! Perfect day for rum tasting at indoor distilleries."
            elif 300 <= weather_id < 500:
                special = "🌧️ Light showers - ideal for rainforest baths and spice plantation tours!"
            elif 500 <= weather_id < 600:
                special = "☔ Rainy day - great for museum hopping or cooking classes!"
            elif 600 <= weather_id < 700:
                special = "❄️ Cool breezes - enjoy cozy cafes and cultural sites!"
            elif 700 <= weather_id < 800:
                special = "🌫️ Misty magic - excellent for photography at scenic viewpoints!"
            elif weather_id == 800:
                special = "☀️ Perfect beach weather! Time for snorkeling and sunbathing."
            else:
                special = "☁️ Cloudy skies - ideal for hiking without the Caribbean heat!"
            return {
                "location": location,
                "date": target_date if target_date else "today",
                "weather": weather_main,
                "temperature": temp,
                "humidity": humidity,
                "special_response": special
            }
        except Exception as e:
            return {"error": f"Weather fetch failed: {str(e)}"}

    def search_destination_images(self, query: str):
        return [{"url": f"https://example.com/{query.replace(' ', '_')}.jpg"}]

    def create_itinerary_with_pdf(self, details: dict):
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
    id="google/gemini-2.5-flash",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    extra_headers={
        "HTTP-Referer": os.getenv('SITE_URL', 'https://tropictrek.com'),
        "X-Title": os.getenv('SITE_NAME', 'TropicTrek')
    }
)

agent = Agent(
    model=openrouter_model,
    tools=[tropictrek_toolkit, duckduckgo, searxng],
    instructions=(
        "You are TropicTrek, a specialized tourism assistant for Eastern Caribbean Currency Union (ECCU) countries. "
        "Use the following tools:\n"
        "- DuckDuckGo: Search for current information\n"
        "- get_ecbb_weather: Check weather forecasts for ECCU islands (max 10 days ahead)\n"
        "- search_destination_images: Show beautiful destination photos\n"
        "- create_itinerary_with_pdf: Generate personalized itineraries\n"
        "- SearxNG: Alternative image search\n\n"
        "When users ask about weather, use get_ecbb_weather with location and optional date (YYYY-MM-DD format). "
        "Be enthusiastic about Caribbean culture and always ask for traveler's name to personalize itineraries."
    ),
    system_message=(
        "You are TropicTrek, a helpful tourism agent specialized in ECCU countries travel planning. "
        "ECCU countries: Antigua & Barbuda, Dominica, Grenada, St. Kitts & Nevis, St. Lucia, St. Vincent & the Grenadines.\n\n"
        "Weather Tool:\n"
        "- Use get_ecbb_weather(location, [date]) for weather forecasts\n"
        "- Date format: YYYY-MM-DD (optional, default is today)\n"
        "- Max forecast: 10 days\n\n"
        "Always provide special Caribbean weather advice from the tool response. "
        "For images, prefer search_destination_images. For itineraries, use create_itinerary_with_pdf."
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
        "I gan help with weather forecasts, itinerary planning, and destination recommendations for islands like:\n"
        "- St. Lucia\n- Grenada\n- Dominica\n- Antigua & Barbuda\n- St. Kitts & Nevis\n- St. Vincent & the Grenadines\n\n"
        "What kin'a Caribbean experience you looking for?",
        stream=True,
        markdown=True
    )

    while True:
        user_input = input("\n🏝️ You: ")
        if user_input.lower() in {"exit", "quit", "bye", "goodbye", "later"}:
            print("\n🌺 Thank you for using TropicTrek! Have an amazing Caribbean adventure! 🌺")
            break
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
                    print(
                        f"TropicTrek 🤖: Weather in {weather_info['location']} on {weather_info['date']}:\n"
                        f"- Condition: {weather_info['weather']}\n"
                        f"- Temperature: {weather_info['temperature']}°C\n"
                        f"- Humidity: {weather_info['humidity']}%\n"
                        f"{weather_info['special_response']}"
                    )
            else:
                print("TropicTrek 🤖: Please specify an ECCB island for the weather info.")
        else:
            await agent.aprint_response(
                user_input,
                stream=True,
                markdown=True
            )


if __name__ == "__main__":
    asyncio.run(main())
