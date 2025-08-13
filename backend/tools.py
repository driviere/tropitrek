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
                self.get_ecbb_weather
            ],
            **kwargs
        )
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY'),
        )
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')

    async def get_ecbb_weather(self, location: str, target_date: str = None) -> str:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.openweather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return f"Unable to fetch weather for {location}."
            data = response.json()
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            return f"Weather in {location}: {weather_desc}, {temp}°C (feels like {feels_like}°C), humidity {humidity}%, wind speed {wind_speed} m/s."
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    async def create_itinerary_with_pdf(
        self, 
        destination: str, 
        traveler_name: str,
        travel_style: str, 
        days: int = 3, 
        interests: str = "", 
        budget: str = "moderate"
    ) -> str:
        logger.info(f"Creating itinerary for {traveler_name} - {destination} ({days} days)")
        try:
            weather_info = ""
            if days <= 10:
                weather_info = await self.get_ecbb_weather(destination)
            itinerary_content = await self._generate_itinerary_content(
                destination, traveler_name, travel_style, days, interests, budget
            )
            if weather_info:
                itinerary_content = f"{weather_info}\n\n{itinerary_content}"
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
        system_prompt = """
You are an expert travel planner specializing in creating detailed, personalized travel itineraries. Your expertise covers all destinations worldwide, with deep knowledge of local attractions, culture, cuisine, transportation, accommodations, and practical travel information.

When creating itineraries, you must:

1. Create comprehensive day-by-day schedules with specific times, activities, and locations
2. Include practical details like transportation, costs, opening hours, and booking requirements  
3. Provide local insights including hidden gems, cultural etiquette, and insider tips
4. Consider the traveler's profile - tailor recommendations to their style, interests, and budget
5. Include essential information like currency, language, safety tips, and emergency contacts
6. Format for PDF readability using clear headers, bullet points, and organized sections
        """
        user_prompt = f"""
Create a detailed {days}-day travel itinerary for {traveler_name} visiting {destination}.

Traveler Details:
- Name: {traveler_name}
- Travel Style: {travel_style}
- Budget Level: {budget}
- Special Interests: {interests if interests else "General travel experience"}
- Trip Duration: {days} days
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
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TropicTrek_Itinerary_{traveler_name.replace(' ', '_')}_{destination.replace(' ', '_')}_{timestamp}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2E8B57'),
            alignment=1
        )
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#1E90FF'),
        )
        story.append(Paragraph("🌴 TropicTrek Itinerary 🌴", title_style))
        story.append(Spacer(1, 20))
        trip_details = f"""
        <b>Traveler:</b> {traveler_name}<br/>
        <b>Destination:</b> {destination.title()}<br/>
        <b>Duration:</b> {days} days<br/>
        <b>Travel Style:</b> {travel_style}<br/>
        <b>Generated:</b> {datetime.datetime.now().strftime("%B %d, %Y")}<br/>
        """
        story.append(Paragraph(trip_details, styles['Normal']))
        story.append(Spacer(1, 30))
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            if line.startswith('##'):
                story.append(Paragraph(line.replace('##', '').strip(), header_style))
            elif line.startswith('#'):
                story.append(Paragraph(line.replace('#', '').strip(), styles['Heading3']))
            elif line.startswith('**') and line.endswith('**'):
                story.append(Paragraph(f"<b>{line[2:-2]}</b>", styles['Normal']))
            else:
                story.append(Paragraph(line, styles['Normal']))
        story.append(PageBreak())
        story.append(Paragraph("🌺 Have an Amazing Caribbean Adventure! 🌺", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Generated by TropicTrek - Your AI Caribbean Travel Assistant", styles['Italic']))
        doc.build(story)
        logger.info(f"PDF created: {filename}")
        return filename

    async def search_destination_images(self, query: str, count: int = 3) -> str:
        logger.info(f"Searching for images: {query}")
        if not self.unsplash_access_key:
            return "🖼️ Image search is currently unavailable. Please configure the Unsplash API key."
        try:
            count = min(count, 10)
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
                return f"🖼️ Sorry, I couldn't fetch images for '{query}' right now."
            data = response.json()
            results = data.get('results', [])
            if not results:
<<<<<<< HEAD
                return f"🖼️ No images found for '{query}'. Try a different search term like 'Caribbean beach' or 'tropical island'."
            
            # Extract just the image URLs and return them as a simple list
            image_urls = []
            image_descriptions = []
            
=======
                return f"🖼️ No images found for '{query}'."
            image_response = f"🖼️ **Here are some beautiful images of {query}:**\n\n"
>>>>>>> 2b9e787fe01b22839e1c9dc9bbc6b0802e2e43c9
            for i, image in enumerate(results[:count], 1):
                image_url = image['urls']['regular']
                alt_description = image.get('alt_description', query)
                photographer = image['user']['name']
<<<<<<< HEAD
                
                # Clean and validate the image URL
                if not image_url or not image_url.startswith('http'):
                    logger.error(f"Invalid image URL for image {i}: {image_url}")
                    continue
                
                # Log the image URL for debugging
                logger.info(f"Image {i} URL: {image_url}")
                logger.info(f"Image {i} Alt: {alt_description}")
                
                image_urls.append(image_url)
                image_descriptions.append(f"{alt_description} (Photo by {photographer})")
            
            # Return a simple response with just the URLs for the agent to use
            urls_text = "\n".join(image_urls)
            
            response = f"Found {len(image_urls)} beautiful images of {query}. Here are the image URLs:\n\n{urls_text}\n\nThese images showcase the natural beauty and attractions of the destination."
            
            logger.info(f"Successfully found {len(results)} images for query: {query}")
            logger.info(f"Returning image URLs to agent: {image_urls}")
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while searching for images: {query}")
            return f"🖼️ The image search timed out. Please try again with a simpler search term."
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while searching for images: {e}")
            return f"🖼️ There was a connection issue while searching for images. Please check your internet connection and try again."
            
=======
                photographer_url = image['user']['links']['html']
                image_response += f"**{i}. {alt_description or query}**\n"
                image_response += f"![{alt_description or query}]({image_url})\n"
                image_response += f"*Photo by [{photographer}]({photographer_url}) on Unsplash*\n\n"
            image_response += "✨ *These images should give you a great preview of what to expect!*"
            return image_response
>>>>>>> 2b9e787fe01b22839e1c9dc9bbc6b0802e2e43c9
        except Exception as e:
            return f"🖼️ Error while searching for images: {str(e)}"
