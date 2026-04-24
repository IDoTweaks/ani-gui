import requests

def fetch_anime(query="Bungo Stray Dogs", limit=8):
    """Fetches anime data from the Jikan API."""
    url = f"https://api.jikan.moe/v4/anime?q={query}&sfw=true&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for HTTP errors
        data = response.json().get('data', [])
        
        results = []
        for show in data:
            results.append({
                "title": show.get("title_english") or show.get("title"),
                "image_url": show["images"]["jpg"]["image_url"],
                "synopsis": show.get("synopsis", "No synopsis available.")
            })
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []