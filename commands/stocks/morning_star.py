from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

BASE_URL = "https://morning-star.p.rapidapi.com"
headers = {
    "x-rapidapi-host": "morning-star.p.rapidapi.com",
    "x-rapidapi-key": getenv("MS_API_KEY"),
}

session = requests.Session()
session.headers = headers

def autocomplete(search: str):
    response = session.get(BASE_URL + '/market/v3/auto-complete', params ={ "q": search })
    response.raise_for_status()

    return response.json()

def getFinancials(performanceId: str):
    response = session.get(BASE_URL + '/stock/v2/get-financials', params = {
        "interval": "annual",
        "reportType": "A",
        "performanceId": performanceId,
    })
    response.raise_for_status()

    return response.json()

def getOverview(performanceId: str):
    response = session.get(BASE_URL + '/stock/v2/key-stats/get-overview', params = {
        "performanceId": performanceId,
    })
    response.raise_for_status()

    return response.json()

def getPriceVsFairValue(performanceId: str):
    response = session.get(BASE_URL + '/stock/v2/get-price-fair-value/', params = { "performanceId": performanceId })
    response.raise_for_status()

    return response.json()

def getInstrumentsPrice(instruments: list):
    response = session.get(BASE_URL + '/stock/v2/get-instruments/', params = {
        "instrumentIds": '126.1.' + ',126.1.'.join(instruments)
    })
    response.raise_for_status()

    return response.json()

def getAvgValuation(performanceId: str):
    response = session.get(BASE_URL + '/stock/v2/get-valuation/', params = {
        "performanceId": performanceId
    })
    response.raise_for_status()

    return response.json()