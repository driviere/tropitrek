from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.models.openrouter import OpenRouter
import asyncio

# Agent 1: Scrape all Ghana news
ghana_news_agent = Agent(
    name="Ghana News Scraper Agent",
    role="Scrape and aggregate all news articles from Ghana across multiple sources.",
    model=OpenRouter(id="gpt-4.1", api_key="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"),
    tools=[DuckDuckGoTools()],
    instructions="You are an expert news aggregator. Your job is to scrape   all recent news articles from Ghana, across all topics. Always include sources and provide a concise detail for each article.",
    add_datetime_to_instructions=True,
)

# Agent 2: Filter for developmental news for a specific place in Ghana
place_dev_news_agent = Agent(
    name="Ghana Developmental News Agent",
    role="Filter and provide only developmental news for a specific place in Ghana as requested by the user.",
    model=OpenRouter(id="gpt-4.1", api_key="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"),
    tools=[DuckDuckGoTools()],
    instructions="You are a specialized news agent. Your task is to extract all recent developmental news about a specific place in Ghana (e.g., Accra, Kumasi, Tamale). Always include sources and provide a concise summary and the nes should be recent."
    "NOTE: The developmental news should include the following: Amenities(eg. schools, hospitals, roads, etc), Industries(eg. mining, agriculture, manufacturing, etc).",
    add_datetime_to_instructions=True,
)

# Team: Coordinate Ghana news and developmental news agents
ghana_dev_news_team = Team(
    name="Ghana Developmental News Team",
    mode="coordinate",
    model=OpenRouter(id="gpt-4.1", api_key="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"),
    members=[ghana_news_agent, place_dev_news_agent],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Collaborate to provide comprehensive, up-to-date news coverage about Ghana, with a focus on developmental news (infrastructure, education, health, technology, etc.).",
        "When a user requests news for a specific place, ensure the response is filtered for developmental topics relevant to that location.",
        "Summarize news clearly, include sources, and present findings in a structured, easy-to-follow format.",
        "Only output the final consolidated news , not individual agent responses.",
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="The team has provided a complete, well-sourced summary of Ghanaian news with a clear focus on developmental topics, and has addressed any user-specified location requests.",
)

if __name__ == "__main__":
    # Example: Get all developmental news for Accra
    while True:
        user_input = input("\n🏝️ You: ")

        ghana_dev_news_team.print_response(
            user_input,
            stream=True,
            show_full_reasoning=True,
            stream_intermediate_steps=True,
        )
    