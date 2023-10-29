import requests
import json


class Tmdb(object):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    def search_movie(self, name: str, country: str, show_max: int) -> str:
        if show_max > 10:
            show_max = 10
        if show_max < 3:
            show_max = 3

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.__api_key}",
        }
        query = {
            "query": name,
            "include_adult": "true",
            "language": "en-US",
            "page": "1",
            "region": country,
        }
        url = f"https://api.themoviedb.org/3/search/movie"
        response = requests.get(url, params=query, headers=headers)
        if not response.ok:
            return f"Nu am găsit nimic pentru {name} în {country}"

        results = json.loads(response.text)['results']
        if len(results)==0:
            return f"Nu am găsit nimic pentru {name} în {country}. Poate trebuia folosit /tv {name}?"


        url = "https://api.themoviedb.org/3/movie/335977?append_to_response=watch%2Fproviders&language=en-US"

    def search_tv(self, name: str, show_max: int):
        if show_max > 10:
            show_max = 10
        if show_max < 3:
            show_max = 3
