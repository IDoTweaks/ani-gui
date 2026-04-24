import requests

def fetch_anime(query="Bungo Stray Dogs", limit=12):
    """Fetches anime data from the Jikan API, sorted by popularity."""
    url = f"https://api.jikan.moe/v4/anime?q={query}&sfw=true&limit={limit}&order_by=members&sort=desc"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json().get('data', [])
        
        results = []
        for show in data:
            # FIX: We use the default Romaji title because ani-cli scrapes sites
            # that usually don't use localized English titles or colons.
            results.append({
                "title": show.get("title"), 
                "image_url": show["images"]["jpg"]["image_url"],
                "synopsis": show.get("synopsis", "No synopsis available.")
            })
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []