import requests
import json


class Tmdb(object):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    def search_movie(self, name: str, country: str, show_max: int) -> list[str]:
        if show_max > 9:
            show_max = 9
        if show_max < 3:
            show_max = 3

        country = country.upper()

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
            return [
                f"Nu am găsit nimic pentru {name} în {country} din cauza unei erori: {response.reason}"
            ]

        results = json.loads(response.text)["results"]
        if len(results) == 0:
            return [
                f"Nu am găsit nimic pentru {name} în {country}. Poate trebuia folosit /tv {name}?"
            ]

        answer: list[str] = []

        for i in range(min(show_max, len(results))):
            query = {"append_to_response": "watch/providers", "language": "en-US"}
            movie_id = results[i]["id"]
            title = results[i]["original_title"]
            release = results[i]["release_date"][:4]
            overview = results[i]["overview"]
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"

            answer.append(f"{i+1}. {title} ({release})")
            answer.append(f"  {overview}")
            response = requests.get(url, params=query, headers=headers)
            if response.ok:
                streaming_info = json.loads(response.text)["watch/providers"]["results"]
                if country in streaming_info and "flatrate" in streaming_info[country]:
                    services: list[str] = []
                    for item in streaming_info[country]["flatrate"]:
                        services.append(item["provider_name"])
                    srvlist = ", ".join(services)
                    link = streaming_info[country]["link"]
                    answer.append(f"[Streaming]({link}): {srvlist}")
                else:
                    answer.append(f"No streaming in {country}")
            answer.append("")

        return answer

    def search_tv(self, name: str, country: str, show_max: int) -> list[str]:
        if show_max > 9:
            show_max = 9
        if show_max < 3:
            show_max = 3

        country = country.upper()

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
        url = f"https://api.themoviedb.org/3/search/tv"
        response = requests.get(url, params=query, headers=headers)
        if not response.ok:
            return [
                f"Nu am găsit nimic pentru {name} în {country} din cauza unei erori: {response.reason}"
            ]

        results = json.loads(response.text)["results"]
        if len(results) == 0:
            return [
                f"Nu am găsit nimic pentru {name} în {country}. Poate trebuia folosit /movie {name}?"
            ]

        answer: list[str] = []

        for i in range(min(show_max, len(results))):
            query = {"append_to_response": "watch/providers", "language": "en-US"}
            series_id = results[i]["id"]
            title = results[i]["original_name"]
            release = results[i]["first_air_date"][:4]
            overview = results[i]["overview"]
            url = f"https://api.themoviedb.org/3/tv/{series_id}"

            answer.append(f"{i+1}. {title} ({release})")
            answer.append(f"  {overview}")
            response = requests.get(url, params=query, headers=headers)
            if response.ok:
                streaming_info = json.loads(response.text)["watch/providers"]["results"]
                if country in streaming_info and "flatrate" in streaming_info[country]:
                    services: list[str] = []
                    for item in streaming_info[country]["flatrate"]:
                        services.append(item["provider_name"])
                    srvlist = ", ".join(services)
                    link = streaming_info[country]["link"]
                    answer.append(f"[Streaming]({link}): {srvlist}")
                else:
                    answer.append(f"No streaming in {country}")
            answer.append("")

        return answer
