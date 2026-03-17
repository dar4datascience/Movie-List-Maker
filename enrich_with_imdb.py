import json
import requests
import time
from typing import Optional

def get_imdb_id_from_omdb(title: str, api_key: str) -> Optional[dict]:
    """
    Fetch IMDB ID using OMDB API.
    Get your free API key from: http://www.omdbapi.com/apikey.aspx
    """
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": api_key,
        "t": title,
        "type": "movie"  # Can also be "series"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("Response") == "True":
            return {
                "imdbID": data.get("imdbID", ""),
                "omdbID": data.get("imdbID", ""),  # OMDB uses same ID as IMDB
                "year": data.get("Year", ""),
                "type": data.get("Type", "")
            }
        else:
            # Try as series if movie search fails
            params["type"] = "series"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("Response") == "True":
                return {
                    "imdbID": data.get("imdbID", ""),
                    "omdbID": data.get("imdbID", ""),
                    "year": data.get("Year", ""),
                    "type": data.get("Type", "")
                }
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    
    return None

def enrich_movie_list(input_file: str, output_file: str, api_key: str):
    """
    Enrich the movie list JSON with IMDB IDs from OMDB API.
    """
    # Load the existing JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)
    
    print(f"Processing {len(movies)} titles...")
    
    # Process each movie
    for i, movie in enumerate(movies):
        title = movie["title"]
        print(f"[{i+1}/{len(movies)}] Fetching: {title}")
        
        # Skip if already has IMDB ID
        if movie.get("imdbID"):
            print(f"  ✓ Already has IMDB ID: {movie['imdbID']}")
            continue
        
        # Fetch IMDB ID
        result = get_imdb_id_from_omdb(title, api_key)
        
        if result:
            movie["imdbID"] = result["imdbID"]
            movie["omdbID"] = result["omdbID"]
            movie["year"] = result.get("year", "")
            movie["type"] = result.get("type", "")
            print(f"  ✓ Found: {result['imdbID']} ({result.get('year', 'N/A')})")
        else:
            print(f"  ✗ Not found")
        
        # Save progress after every 10 titles
        if (i + 1) % 10 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            print(f"  💾 Progress saved ({i+1}/{len(movies)})")
        
        # Rate limiting - be nice to the API
        time.sleep(0.5)
    
    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete! Enriched data saved to: {output_file}")
    
    # Statistics
    found = sum(1 for m in movies if m.get("imdbID"))
    print(f"\nStatistics:")
    print(f"  Total titles: {len(movies)}")
    print(f"  Found: {found}")
    print(f"  Not found: {len(movies) - found}")

if __name__ == "__main__":
    # Configuration
    INPUT_FILE = "unified_movie_list.json"
    OUTPUT_FILE = "unified_movie_list_enriched.json"
    
    # You need to get your free API key from: http://www.omdbapi.com/apikey.aspx
    API_KEY = input("Enter your OMDB API key (get free key at http://www.omdbapi.com/apikey.aspx): ").strip()
    
    if not API_KEY:
        print("❌ Error: API key is required!")
        exit(1)
    
    enrich_movie_list(INPUT_FILE, OUTPUT_FILE, API_KEY)
