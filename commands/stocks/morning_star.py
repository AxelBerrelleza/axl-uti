from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

BASE_URL = "https://morning-star.p.rapidapi.com/market/v3"
headers = {
    "x-rapidapi-host": "morning-star.p.rapidapi.com",
    "x-rapidapi-key": getenv("MS_API_KEY"),
}

session = requests.Session()
session.headers = headers

def autocomplete(search: str):
    response = session.get(BASE_URL + '/auto-complete', params={"q": search})
    response.raise_for_status()

    return response.json()