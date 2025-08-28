import requests
import json

def test_news_api(place):
    """Test the news API with a specific place"""
    url = "http://localhost:8000/news"
    payload = {"place": place}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Print the response
        print(f"\nDevelopmental News for {place}:\n")
        result = response.json()
        print(result["news"])
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Make sure the API server is running before executing this script
    place = input("Enter a place in Ghana to get developmental news for: ")
    test_news_api(place)