import json
import pandas as pd

def create_csv():
    with open('unified_movie_list.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)
    
    df = pd.DataFrame(movies)
    df.to_csv('movie_list.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    create_csv()
