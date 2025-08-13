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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
import datetime

load_dotenv()

# Get OpenWeather API key from environment
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')


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
🌴 **Your {destination.title()} Itinerary is Ready!** 🌴

**Traveler:** {traveler_name}
**Destination:** {destination.title()}
**Duration:** {days} days
**Style:** {travel_style}
**Budget:** {budget.title()}

{itinerary_content}

📄 **PDF Generated:** `{pdf_filename}`

Your complete itinerary has been saved as a PDF for easy download and offline access during your trip!
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
You are an expert travel planner specializing in creating clean, professional travel itineraries for Caribbean destinations. 

Create itineraries using proper markdown formatting that will look professional both in chat and PDF format.

Use this exact markdown structure:

# Travel Itinerary

## Trip Overview
- **Destination:** [Location]
- **Duration:** [X] days
- **Travel Style:** [Style]
- **Budget:** [Budget Level]

## Day-by-Day Schedule

### Day 1 - Arrival & Exploration
**Morning (9:00 AM)**
- Arrive at airport
- Check into hotel
- Welcome drink and orientation

**Afternoon (2:00 PM)**
- Visit local market
- Traditional lunch at [Restaurant Name]
- Explore downtown area

**Evening (6:00 PM)**
- Sunset beach walk
- Dinner at seaside restaurant
- Rest and prepare for tomorrow

### Day 2 - Adventure Day
**Morning (8:00 AM)**
- Hiking tour to waterfall
- Guided nature walk
- Photography opportunities

**Afternoon (1:00 PM)**
- Lunch at mountain restaurant
- Swimming at natural pools
- Return journey

**Evening (5:00 PM)**
- Return to hotel
- Relax by pool
- Dinner at hotel restaurant

## Important Information
- **Currency:** Eastern Caribbean Dollar (XCD)
- **Emergency Contact:** [Local number]
- **Weather:** [Current conditions]
- **Tips:** [Local customs and advice]

Use this exact format with proper markdown headers, bullet points, and bold text for times and activities.
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
        """Create a clean, professional PDF from the itinerary content"""
        
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TropicTrek_Itinerary_{traveler_name.replace(' ', '_')}_{destination.replace(' ', '_')}_{timestamp}.pdf"
        
        # Create PDF document with margins
        doc = SimpleDocTemplate(
            filename, 
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles for professional look
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            textColor=HexColor('#1E3A8A'),  # Professional blue
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=30,
            textColor=HexColor('#6B7280'),  # Gray
            alignment=1,  # Center alignment
            fontName='Helvetica'
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=HexColor('#1E3A8A'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#E5E7EB'),
            borderPadding=10,
            backColor=HexColor('#F8FAFC')
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            fontName='Helvetica'
        )
        
        # Header with logo placeholder and title
        story.append(Paragraph("Travel Itinerary", title_style))
        story.append(Paragraph(f"{destination.title()}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Traveler Information Table
        traveler_data = [
            ['TRAVELER INFORMATION', ''],
            ['Name of Traveler', traveler_name],
            ['Destination', destination.title()],
            ['Duration', f'{days} days'],
            ['Travel Style', travel_style],
            ['Generated Date', datetime.datetime.now().strftime("%B %d, %Y")]
        ]
        
        traveler_table = Table(traveler_data, colWidths=[2.5*inch, 3*inch])
        traveler_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            
            # Data rows
            ('BACKGROUND', (0, 1), (1, -1), HexColor('#F8FAFC')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (1, -1), 10),
            ('GRID', (0, 0), (1, -1), 1, HexColor('#E5E7EB')),
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (1, -1), 10),
            ('RIGHTPADDING', (0, 0), (1, -1), 10),
            ('TOPPADDING', (0, 0), (1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (1, -1), 8),
        ]))
        
        story.append(traveler_table)
        story.append(Spacer(1, 30))
        
        # Parse and format the itinerary content
        lines = content.split('\n')
        current_day = None
        day_activities = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Main headers (# Travel Itinerary)
            if line.startswith('# '):
                continue  # Skip main title as we already have it
                
            # Section headers (## Trip Overview, ## Day-by-Day Schedule)
            elif line.startswith('## '):
                if day_activities and current_day:
                    # Create table for previous day
                    story.append(self._create_day_table(current_day, day_activities))
                    story.append(Spacer(1, 15))
                    day_activities = []
                    
                section_title = line.replace('## ', '').strip()
                story.append(Paragraph(section_title, section_header_style))
                
            # Day headers (### Day 1 - Arrival & Exploration)
            elif line.startswith('### '):
                if day_activities and current_day:
                    # Create table for previous day
                    story.append(self._create_day_table(current_day, day_activities))
                    story.append(Spacer(1, 15))
                    
                current_day = line.replace('### ', '').strip()
                day_activities = []
                
            # Time periods (**Morning (9:00 AM)**)
            elif line.startswith('**') and line.endswith('**') and ('AM' in line or 'PM' in line):
                time_period = line.replace('**', '').strip()
                day_activities.append(['TIME_HEADER', time_period])
                
            # Activity items (- Activity description)
            elif line.startswith('- '):
                activity = line.replace('- ', '').strip()
                day_activities.append(['ACTIVITY', activity])
                
            # Important information bullets
            elif line.startswith('- **') and line.endswith('**'):
                info_item = line.replace('- **', '').replace('**', '').strip()
                story.append(Paragraph(f"• <b>{info_item}</b>", info_style))
                
            # Regular bullets
            elif line.startswith('- '):
                bullet_text = line.replace('- ', '').strip()
                story.append(Paragraph(f"• {bullet_text}", info_style))
        
        # Add the last day if exists
        if day_activities and current_day:
            story.append(self._create_day_table(current_day, day_activities))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Have an Amazing Caribbean Adventure!", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Generated by TropicTrek - Your AI Caribbean Travel Assistant", subtitle_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Professional PDF created: {filename}")
        return filename
    
    def _create_day_table(self, day_title: str, activities: list) -> Table:
        """Create a professional table for a day's activities with proper text wrapping"""
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        
        styles = getSampleStyleSheet()
        
        # Create custom styles for table content
        time_style = ParagraphStyle(
            'TimeStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1E3A8A'),
            spaceAfter=0
        )
        
        activity_style = ParagraphStyle(
            'ActivityStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            leftIndent=0,
            spaceAfter=2,
            leading=11
        )
        
        # Prepare table data with Paragraph objects for proper text wrapping
        table_data = [
            [Paragraph(day_title, time_style), '']  # Header row
        ]
        
        current_time = None
        for activity_type, content in activities:
            if activity_type == 'TIME_HEADER':
                current_time = content
                table_data.append([Paragraph(current_time, time_style), ''])
            elif activity_type == 'ACTIVITY':
                if current_time:
                    # Use Paragraph for proper text wrapping
                    activity_para = Paragraph(f"• {content}", activity_style)
                    table_data.append(['', activity_para])
                else:
                    activity_para = Paragraph(f"• {content}", activity_style)
                    table_data.append([Paragraph('Activity', time_style), activity_para])
        
        # Create table with optimized column widths for A4 page
        day_table = Table(table_data, colWidths=[1.3*inch, 4.2*inch])
        day_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            
            # Time headers and content
            ('BACKGROUND', (0, 1), (1, -1), HexColor('#F1F5F9')),
            ('GRID', (0, 0), (1, -1), 1, HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (1, -1), 8),
            ('RIGHTPADDING', (0, 0), (1, -1), 8),
            ('TOPPADDING', (0, 0), (1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (1, -1), 8),
        ]))
        
        return day_table

        

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
                
                # Clean and validate the image URL
                if not image_url or not image_url.startswith('http'):
                    logger.error(f"Invalid image URL for image {i}: {image_url}")
                    continue
                
                # Log the image URL for debugging
                logger.info(f"Image {i} URL: {image_url}")
                logger.info(f"Image {i} Alt: {alt_description}")
                
                # Clean alt text for markdown (remove problematic characters)
                clean_alt = (alt_description or query).replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                
                # Add image with markdown format - ensure proper spacing and formatting
                image_response += f"**{i}. {clean_alt}**\n\n"
                image_response += f"![{clean_alt}]({image_url})\n\n"
                image_response += f"*Photo by [{photographer}]({photographer_url}) on Unsplash*\n\n"
            
            image_response += "✨ *These images should give you a great preview of what to expect at your destination!*"
            
            logger.info(f"Successfully found {len(results)} images for query: {query}")
            logger.info(f"Image response being returned: {image_response}")
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