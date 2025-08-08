"""
TropicTrek Toolkit - Single tool for itinerary generation with PDF export
"""

from typing import List, Optional
from agno.agent import Agent
from agno.tools import Toolkit
from agno.utils.log import logger
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import datetime

load_dotenv()


class TropicTrekToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(
            name="tropictrek_toolkit",
            tools=[
                self.create_itinerary_with_pdf,
                self.search_destination_images,
            ],
            **kwargs
        )
        
        # Initialize OpenRouter client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY'),
        )
        
        # Initialize Unsplash API key
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')

    async def create_itinerary_with_pdf(
        self, 
        destination: str, 
        traveler_name: str,
        travel_style: str, 
        days: int = 3, 
        interests: str = "", 
        budget: str = "moderate"
    ) -> str:
        """
        Create a personalized travel itinerary and generate a downloadable PDF.
        
        Args:
            destination (str): Travel destination
            traveler_name (str): Name of the traveler for personalization
            travel_style (str): Travel personality (e.g., "Adventure Seeker", "Relaxation", "Cultural Explorer")
            days (int): Number of days for the trip (default: 3)
            interests (str): Specific interests or activities (optional)
            budget (str): Budget level - "budget", "moderate", or "luxury" (default: "moderate")
            
        Returns:
            str: Success message with PDF file path and itinerary summary
        """
        
        logger.info(f"Creating itinerary for {traveler_name} - {destination} ({days} days)")
        
        try:
            # Generate detailed itinerary using OpenRouter LLM
            itinerary_content = await self._generate_itinerary_content(
                destination, traveler_name, travel_style, days, interests, budget
            )
            
            # Create PDF
            pdf_filename = await self._create_pdf(
                itinerary_content, traveler_name, destination, days, travel_style
            )
            
            return f"""
🌴 **Itinerary Created Successfully!** 🌴

**Traveler:** {traveler_name}
**Destination:** {destination.title()}
**Duration:** {days} days
**Style:** {travel_style}
**Budget:** {budget.title()}

📄 **PDF Generated:** `{pdf_filename}`

Your personalized travel itinerary is ready! The PDF includes detailed day-by-day planning, local recommendations, and practical travel information.

*Download your complete itinerary PDF to take with you on your adventure!* 🏝️
            """
            
        except Exception as e:
            logger.error(f"Error creating itinerary: {e}")
            return f"Sorry, I encountered an error while creating your itinerary: {str(e)}"

    async def _generate_itinerary_content(
        self, destination: str, traveler_name: str, travel_style: str, 
        days: int, interests: str, budget: str
    ) -> str:
        """Generate detailed itinerary content using OpenRouter LLM with comprehensive system prompt"""
        
        system_prompt = """
You are an expert travel planner specializing in creating detailed, personalized travel itineraries. Your expertise covers all destinations worldwide, with deep knowledge of local attractions, culture, cuisine, transportation, accommodations, and practical travel information.

When creating itineraries, you must:

1. **Create comprehensive day-by-day schedules** with specific times, activities, and locations
2. **Include practical details** like transportation, costs, opening hours, and booking requirements  
3. **Provide local insights** including hidden gems, cultural etiquette, and insider tips
4. **Consider the traveler's profile** - tailor recommendations to their style, interests, and budget
5. **Include essential information** like currency, language, safety tips, and emergency contacts
6. **Format for PDF readability** using clear headers, bullet points, and organized sections

Your itineraries should be engaging, informative, and actionable - something a traveler can actually follow and use during their trip.
        """
        
        user_prompt = f"""
Create a detailed {days}-day travel itinerary for {traveler_name} visiting {destination}.

Traveler Details:
- Name: {traveler_name}
- Travel Style: {travel_style}
- Budget Level: {budget}
- Special Interests: {interests if interests else "General travel experience"}
- Trip Duration: {days} days

Please create a comprehensive itinerary that this traveler can actually use during their trip.
        """
        
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": os.getenv('SITE_URL', 'https://tropictrek.com'),
                    "X-Title": os.getenv('SITE_NAME', 'TropicTrek'),
                },
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating itinerary content: {e}")
            return f"Error generating detailed itinerary: {str(e)}"

    async def _create_pdf(
        self, content: str, traveler_name: str, destination: str, days: int, travel_style: str
    ) -> str:
        """Create a formatted PDF from the itinerary content"""
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TropicTrek_Itinerary_{traveler_name.replace(' ', '_')}_{destination.replace(' ', '_')}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2E8B57'),  # Sea Green
            alignment=1  # Center alignment
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#1E90FF'),  # Dodger Blue
        )
        
        # Title page
        story.append(Paragraph("🌴 TropicTrek Itinerary 🌴", title_style))
        story.append(Spacer(1, 20))
        
        # Trip details
        trip_details = f"""
        <b>Traveler:</b> {traveler_name}<br/>
        <b>Destination:</b> {destination.title()}<br/>
        <b>Duration:</b> {days} days<br/>
        <b>Travel Style:</b> {travel_style}<br/>
        <b>Generated:</b> {datetime.datetime.now().strftime("%B %d, %Y")}<br/>
        """
        story.append(Paragraph(trip_details, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Process content and add to PDF
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            # Headers (lines starting with ##)
            if line.startswith('##'):
                story.append(Paragraph(line.replace('##', '').strip(), header_style))
            # Subheaders (lines starting with #)
            elif line.startswith('#'):
                story.append(Paragraph(line.replace('#', '').strip(), styles['Heading3']))
            # Bold text (lines starting with **)
            elif line.startswith('**') and line.endswith('**'):
                story.append(Paragraph(f"<b>{line[2:-2]}</b>", styles['Normal']))
            # Regular text
            else:
                story.append(Paragraph(line, styles['Normal']))
        
        # Footer
        story.append(PageBreak())
        story.append(Paragraph("🌺 Have an Amazing Caribbean Adventure! 🌺", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Generated by TropicTrek - Your AI Caribbean Travel Assistant", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF created: {filename}")
        return filename

        

    async def search_destination_images(self, query: str, count: int = 3) -> str:
        """
        Search for destination images using Unsplash API.
        
        Args:
            query (str): Search query for images (e.g., "St. Lucia beach", "Grenada waterfall", "Dominica rainforest")
            count (int): Number of images to return (default: 3, max: 10)
            
        Returns:
            str: Formatted response with image URLs and descriptions for display in chat
        """
        
        logger.info(f"Searching for images: {query}")
        
        if not self.unsplash_access_key:
            return "🖼️ Image search is currently unavailable. Please configure the Unsplash API key to view destination photos."
        
        try:
            # Limit count to reasonable number
            count = min(count, 10)
            
            # Make request to Unsplash API
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'per_page': count,
                'orientation': 'landscape',
                'content_filter': 'high',
                'client_id': self.unsplash_access_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Unsplash API error: {response.status_code}")
                return f"🖼️ Sorry, I couldn't fetch images for '{query}' right now. Please try again later."
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return f"🖼️ No images found for '{query}'. Try a different search term like 'Caribbean beach' or 'tropical island'."
            
            # Format response with images
            image_response = f"🖼️ **Here are some beautiful images of {query}:**\n\n"
            
            for i, image in enumerate(results[:count], 1):
                # Get image URLs (using regular size for better loading)
                image_url = image['urls']['regular']
                alt_description = image.get('alt_description', query)
                photographer = image['user']['name']
                photographer_url = image['user']['links']['html']
                
                # Add image with markdown format
                image_response += f"**{i}. {alt_description or query}**\n"
                image_response += f"![{alt_description or query}]({image_url})\n"
                image_response += f"*Photo by [{photographer}]({photographer_url}) on Unsplash*\n\n"
            
            image_response += "✨ *These images should give you a great preview of what to expect at your destination!*"
            
            logger.info(f"Successfully found {len(results)} images for query: {query}")
            return image_response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while searching for images: {query}")
            return f"🖼️ The image search timed out. Please try again with a simpler search term."
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while searching for images: {e}")
            return f"🖼️ There was a connection issue while searching for images. Please check your internet connection and try again."
            
        except Exception as e:
            logger.error(f"Unexpected error in image search: {e}")
            return f"🖼️ Sorry, I encountered an unexpected error while searching for images of '{query}'. Please try again."




    async def get_ecbb_weather(self, location: str, target_date: str = None) -> dict:
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