# TropiTrek Ghana Development News API

This API provides access to the latest developmental news from Ghana for specific locations. It leverages an AI agent system to gather and filter news articles focused on development topics such as infrastructure, education, health, technology, and more.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the API server:

```bash
python api.py
```

The server will start on http://localhost:8000

## API Endpoints

### GET /

Welcome endpoint that confirms the API is running.

**Response:**
```json
{
  "message": "Welcome to TropiTrek Ghana Development News API"
}
```

### POST /news

Retrieve developmental news for a specific place in Ghana.

**Request Body:**
```json
{
  "place": "Accra"
}
```

**Response:**
```json
{
  "news": "[Formatted news content with sources]"
}
```

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/news" \
     -H "Content-Type: application/json" \
     -d '{"place":"Accra"}'
```

### Using Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/news",
    json={"place": "Accra"}
)

print(response.json())
```

## Notes

- The API uses the Agno framework to coordinate multiple AI agents for comprehensive news gathering and filtering.
- Results include sources and concise summaries of developmental news.
- The response is formatted in Markdown for better readability.
