from typing import List, Optional, Callable
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
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import threading
import time
import asyncio

load_dotenv()

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant with default settings"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.stop_listening = None
        self.on_voice_callback = None
        self.language = 'en-US'
        self.voice_temp_dir = tempfile.mkdtemp()
        pygame.mixer.init()
        
        # Adjust for ambient noise automatically
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def set_language(self, language_code: str):
        """Set the language for both speech recognition and synthesis"""
        self.language = language_code

    def speak(self, text: str, blocking: bool = False):
        """Convert text to speech and play it"""
        try:
            tts = gTTS(text=text, lang=self.language[:2])
            temp_file = os.path.join(self.voice_temp_dir, 'temp_voice.mp3')
            tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            if blocking:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Error in speech synthesis: {e}")

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for voice input and return transcribed text"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
            print("Processing speech...")
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.WaitTimeoutError:
            print("Listening timed out")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None

    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start listening continuously in the background"""
        self.on_voice_callback = callback
        self.is_listening = True
        
        def listen_thread():
            while self.is_listening:
                text = self.listen()
                if text and self.on_voice_callback:
                    self.on_voice_callback(text)
        
        threading.Thread(target=listen_thread, daemon=True).start()

    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.is_listening = False

    def cleanup(self):
        """Clean up resources"""
        try:
            pygame.mixer.quit()
            for file in os.listdir(self.voice_temp_dir):
                os.remove(os.path.join(self.voice_temp_dir, file))
            os.rmdir(self.voice_temp_dir)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class TropicTrekToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(
            name="tropictrek_toolkit",
            tools=[
                self.create_itinerary_with_pdf,
                self.search_destination_images,
                self.get_ecbb_weather,
                self.voice_speak,
                self.voice_listen
            ],
            **kwargs
        )
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY'),
        )
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.voice_assistant = VoiceAssistant()

    async def get_ecbb_weather(self, location: str, date: str = None) -> str:
        """Get weather for a location with flexible date input"""
        try:
            # Handle date specification
            date_param = ""
            if date:
                # Support natural language date formats
                if "today" in date.lower():
                    date_param = "&cnt=1"
                elif "tomorrow" in date.lower():
                    date_param = "&cnt=2"
                elif "week" in date.lower() or "7 days" in date.lower():
                    date_param = "&cnt=7"
                elif "5 days" in date.lower():
                    date_param = "&cnt=5"
                else:
                    # Try to parse as a specific date
                    try:
                        # Attempt to parse various date formats
                        parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                        days_diff = (parsed_date - datetime.date.today()).days
                        if 0 <= days_diff <= 16:
                            date_param = f"&cnt={days_diff+1}"
                        else:
                            return "Weather forecast is only available for up to 16 days in the future."
                    except ValueError:
                        # Handle other natural language formats
                        return "Please specify a date like 'today', 'tomorrow', 'next Friday', or 'in 5 days'."
            
            # Use forecast API
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={self.openweather_api_key}&units=metric{date_param}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return f"Unable to fetch weather for {location}."
            
            data = response.json()
            
            # Process current weather if no date specified
            if not date:
                weather_desc = data['list'][0]['weather'][0]['description']
                temp = data['list'][0]['main']['temp']
                feels_like = data['list'][0]['main']['feels_like']
                humidity = data['list'][0]['main']['humidity']
                wind_speed = data['list'][0]['wind']['speed']
                return f"Current weather in {location}: {weather_desc}, {temp}°C (feels like {feels_like}°C), humidity {humidity}%, wind speed {wind_speed} m/s.\n\nCaribbean Tip: Always check for tropical storm warnings during hurricane season (June-November)."
            
            # Process forecast
            forecast = []
            for item in data['list']:
                forecast_time = item['dt_txt']
                weather_desc = item['weather'][0]['description']
                temp = item['main']['temp']
                forecast.append(f"{forecast_time}: {weather_desc}, {temp}°C")
            
            return (
                f"Weather forecast for {location}:\n" +
                "\n".join(forecast) +
                "\n\nCaribbean Tip: Always check for tropical storm warnings during hurricane season (June-November)."
            )
            
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
                return f"🖼️ No images found for '{query}'."
            image_response = f"🖼️ **Here are some beautiful images of {query}:**\n\n"
            for i, image in enumerate(results[:count], 1):
                image_url = image['urls']['regular']
                alt_description = image.get('alt_description', query)
                photographer = image['user']['name']
                photographer_url = image['user']['links']['html']
                image_response += f"**{i}. {alt_description or query}**\n"
                image_response += f"![{alt_description or query}]({image_url})\n"
                image_response += f"*Photo by [{photographer}]({photographer_url}) on Unsplash*\n\n"
            image_response += "✨ *These images should give you a great preview of what to expect!*"
            return image_response
        except Exception as e:
            return f"🖼️ Error while searching for images: {str(e)}"

    # Voice Assistant Tools
    async def voice_speak(self, text: str) -> str:
        """Speak the given text aloud. Input is the text to speak."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.voice_assistant.speak, text, False)
        return f"Spoke: {text[:50]}..."
    
    async def voice_listen(self, timeout: int = 5) -> str:
        """Listen for voice input and return transcribed text. 
        Optional timeout parameter (default 5 seconds)."""
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self.voice_assistant.listen, timeout, 10)
        return text or "No speech detected"
