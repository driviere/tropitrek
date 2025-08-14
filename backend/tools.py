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
You are an expert travel planner specializing in creating simple, tabular travel itineraries for Caribbean destinations.

Create itineraries in a clean, structured format that will be converted to professional PDF tables.

Use this exact structure for the itinerary content:

TRAVELER INFORMATION
Name: [Traveler Name]
Destination: [Location]
Duration: [X] days
Travel Style: [Style]
Budget: [Budget Level]
Generated: [Current Date]

ITINERARY SCHEDULE
Day 1 - [Theme/Focus]
Morning (9:00 AM) | Activity 1 | Location/Details
Afternoon (2:00 PM) | Activity 2 | Location/Details  
Evening (6:00 PM) | Activity 3 | Location/Details

Day 2 - [Theme/Focus]
Morning (8:00 AM) | Activity 1 | Location/Details
Afternoon (1:00 PM) | Activity 2 | Location/Details
Evening (5:00 PM) | Activity 3 | Location/Details

IMPORTANT INFORMATION
Currency | Eastern Caribbean Dollar (XCD)
Emergency | Local emergency number
Weather | Current conditions and tips
Local Tips | Cultural customs and advice

Keep activities concise and specific. Focus on actual locations, restaurants, and attractions. Each activity should be one clear, actionable item.
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
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
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
        
        # Professional title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            textColor=HexColor('#1E3A8A'),
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        # Header
        story.append(Paragraph("Travel Itinerary", title_style))
        story.append(Paragraph(f"{destination.title()}", title_style))
        story.append(Spacer(1, 20))
        
        # Parse content to extract structured data
        lines = content.split('\n')
        traveler_info = {}
        schedule_data = []
        important_info = {}
        current_section = None
        current_day = None
        
        # Default traveler info if not found in content
        traveler_info = {
            'Name': traveler_name,
            'Destination': destination.title(),
            'Duration': f'{days} days',
            'Travel Style': travel_style,
            'Generated': datetime.datetime.now().strftime("%B %d, %Y")
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line == "TRAVELER INFORMATION":
                current_section = "traveler"
                continue
            elif line == "ITINERARY SCHEDULE":
                current_section = "schedule"
                continue
            elif line == "IMPORTANT INFORMATION":
                current_section = "important"
                continue
                
            if current_section == "traveler" and ":" in line:
                key, value = line.split(":", 1)
                traveler_info[key.strip()] = value.strip()
                
            elif current_section == "schedule":
                if line.startswith("Day ") and " - " in line:
                    current_day = line
                    # Create day header as a Paragraph that spans all columns
                    day_para = Paragraph(current_day, ParagraphStyle(
                        'DayHeader',
                        parent=styles['Normal'],
                        fontSize=11,
                        fontName='Helvetica-Bold',
                        textColor=HexColor('#FFFFFF'),
                        alignment=1
                    ))
                    schedule_data.append([day_para, "", ""])
                elif "|" in line and current_day:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        time = parts[0].strip()
                        activity = parts[1].strip()
                        location = parts[2].strip()
                        # Wrap long text in Paragraph objects for proper table cell handling
                        time_para = Paragraph(time, ParagraphStyle(
                            'TimeStyle',
                            parent=styles['Normal'],
                            fontSize=9,
                            fontName='Helvetica-Bold',
                            leading=11,
                            leftIndent=3,
                            rightIndent=3,
                            wordWrap='CJK'
                        ))
                        activity_para = Paragraph(activity, ParagraphStyle(
                            'ActivityStyle',
                            parent=styles['Normal'],
                            fontSize=9,
                            fontName='Helvetica',
                            leading=11,
                            leftIndent=3,
                            rightIndent=3,
                            wordWrap='CJK'
                        ))
                        location_para = Paragraph(location, ParagraphStyle(
                            'LocationStyle',
                            parent=styles['Normal'],
                            fontSize=9,
                            fontName='Helvetica',
                            leading=11,
                            leftIndent=3,
                            rightIndent=3,
                            wordWrap='CJK'
                        ))
                        schedule_data.append([time_para, activity_para, location_para])
                        
            elif current_section == "important" and "|" in line:
                key, value = line.split("|", 1)
                important_info[key.strip()] = value.strip()
        
        # If no schedule data found, create a simple fallback
        if not schedule_data:
            for day in range(1, days + 1):
                day_header = f"Day {day} - Caribbean Adventure"
                schedule_data.append([day_header, "", ""])
                schedule_data.append([
                    Paragraph("Morning (9:00 AM)", styles['Normal']),
                    Paragraph("Explore local attractions", styles['Normal']),
                    Paragraph("Various locations", styles['Normal'])
                ])
                schedule_data.append([
                    Paragraph("Afternoon (2:00 PM)", styles['Normal']),
                    Paragraph("Cultural activities", styles['Normal']),
                    Paragraph("Local venues", styles['Normal'])
                ])
                schedule_data.append([
                    Paragraph("Evening (6:00 PM)", styles['Normal']),
                    Paragraph("Dining and relaxation", styles['Normal']),
                    Paragraph("Restaurant recommendations", styles['Normal'])
                ])
        
        # Default important info if not found
        if not important_info:
            important_info = {
                'Currency': 'Eastern Caribbean Dollar (XCD)',
                'Emergency': '999 (Police), 911 (Fire/Medical)',
                'Weather': 'Tropical climate, 26-30°C',
                'Local Tips': 'Respect local customs, try local cuisine'
            }
        
        # Create Traveler Information Table
        traveler_data = [
            ['TRAVELER INFORMATION', '']
        ]
        
        for key, value in traveler_info.items():
            traveler_data.append([key, value])
        
        traveler_table = Table(traveler_data, colWidths=[2*inch, 3.5*inch])
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
        
        # Create Schedule Table
        if schedule_data:
            schedule_table_data = [
                ['ITINERARY SCHEDULE', '', '']
            ]
            schedule_table_data.extend(schedule_data)
            
            schedule_table = Table(schedule_table_data, colWidths=[1.0*inch, 3.0*inch, 1.5*inch], repeatRows=1)
            schedule_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (2, 0), HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 12),
                ('SPAN', (0, 0), (2, 0)),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                
                # Day headers (rows that start with "Day")
                ('BACKGROUND', (0, 1), (2, -1), HexColor('#F1F5F9')),
                ('FONTNAME', (0, 1), (2, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (2, -1), 9),
                ('GRID', (0, 0), (2, -1), 1, HexColor('#E2E8F0')),
                ('VALIGN', (0, 0), (2, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (2, -1), 8),
                ('RIGHTPADDING', (0, 0), (2, -1), 8),
                ('TOPPADDING', (0, 0), (2, -1), 6),
                ('BOTTOMPADDING', (0, 0), (2, -1), 6),
            ]))
            
            # Style day headers differently - track which rows are day headers
            day_header_rows = []
            for i, row in enumerate(schedule_table_data[1:], 1):
                # Check if this is a day header row (has Paragraph object with empty strings)
                if len(row) == 3 and row[1] == "" and row[2] == "":
                    day_header_rows.append(i)
            
            # Apply styling to day header rows
            for row_idx in day_header_rows:
                schedule_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, row_idx), (2, row_idx), HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, row_idx), (2, row_idx), colors.white),
                    ('FONTNAME', (0, row_idx), (2, row_idx), 'Helvetica-Bold'),
                    ('SPAN', (0, row_idx), (2, row_idx)),
                    ('ALIGN', (0, row_idx), (2, row_idx), 'CENTER'),
                ]))
            
            story.append(schedule_table)
            story.append(Spacer(1, 30))
        
        # Create Important Information Table
        if important_info:
            info_data = [
                ['IMPORTANT INFORMATION', '']
            ]
            
            for key, value in important_info.items():
                info_data.append([key, value])
            
            info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
            info_table.setStyle(TableStyle([
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
            
            story.append(info_table)
        
        # Footer
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6B7280'),
            alignment=1
        )
        story.append(Paragraph("Generated by TropicTrek - Your AI Caribbean Travel Assistant", footer_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Professional tabular PDF created: {filename}")
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
                return f"🖼️ No images found for '{query}'. Try a different search term like 'Caribbean beach' or 'tropical island'."
            
            # Extract just the image URLs and return them as a simple list
            image_urls = []
            image_descriptions = []
            
            for i, image in enumerate(results[:count], 1):
                image_url = image['urls']['regular']
                alt_description = image.get('alt_description', query)
                photographer = image['user']['name']
                
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
            
        except Exception as e:
            return f"🖼️ Error while searching for images: {str(e)}"
