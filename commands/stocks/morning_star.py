from enum import StrEnum
from dotenv import load_dotenv
from os import getenv
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
from commands.errors import (
    APIError,
    APIAuthError,
    APIRateLimitError,
    APIServerError,
    NetworkError,
)

load_dotenv()

BASE_URL = "https://morning-star.p.rapidapi.com"
headers = {
    "x-rapidapi-host": "morning-star.p.rapidapi.com",
    "x-rapidapi-key": getenv("MS_API_KEY"),
}
class Endpoints(StrEnum):
    __stocks: str = '/stock/v2'
    OVERVIEW = BASE_URL + __stocks + '/key-stats/get-overview/'
    INSTRUMENTS = BASE_URL + __stocks + '/get-instruments/'
    AVG_VALUATION = BASE_URL + __stocks + '/get-valuation/'
    COMPETITORS = BASE_URL + __stocks + '/get-competitors'
    FINANCIAL_HEALTH = BASE_URL + __stocks + '/key-stats/get-financial-health'

session = requests.Session()
session.headers = headers


def _api_request(endpoint: str, params: dict | None = None) -> dict:
    try:
        response = session.get(endpoint, params=params or {})
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        status = e.response.status_code
        if status in (401, 403):
            raise APIAuthError(status, endpoint)
        elif status == 429:
            raise APIRateLimitError(endpoint)
        elif status >= 500:
            raise APIServerError(status, endpoint)
        else:
            raise APIError(status, endpoint, str(e))
    except (ConnectionError, Timeout) as e:
        raise NetworkError(endpoint, e)
    except KeyError as e:
        raise APIError(0, endpoint, f"Missing expected field in response: {e}")


def autocomplete(search: str):
    return _api_request(
        BASE_URL + '/market/v3/auto-complete',
        params={"q": search},
    )


def getFinancials(performanceId: str):
    return _api_request(
        BASE_URL + '/stock/v2/get-financials',
        params={
            "interval": "annual",
            "reportType": "A",
            "performanceId": performanceId,
        },
    )


def getOverview(performanceId: str):
    return _api_request(
        Endpoints.OVERVIEW,
        params={"performanceId": performanceId},
    )


def getPriceVsFairValue(performanceId: str):
    return _api_request(
        BASE_URL + '/stock/v2/get-price-fair-value/',
        params={"performanceId": performanceId},
    )


def getInstrumentsPrice(instruments: list):
    return _api_request(
        Endpoints.INSTRUMENTS,
        params={"instrumentIds": '126.1.' + ',126.1.'.join(instruments)},
    )


def getAvgValuation(performanceId: str):
    return _api_request(
        Endpoints.AVG_VALUATION,
        params={"performanceId": performanceId},
    )


def getOperatingEfficency(performanceId: str):
    return _api_request(
        BASE_URL + '/stock/v2/key-stats/get-operating-efficiency/',
        params={"performanceId": performanceId},
    )


def getCompetitors(performanceId: str):
    return _api_request(
        Endpoints.COMPETITORS,
        params={"performanceId": performanceId},
    )


def getFinancialHealth(performanceId: str):
    return _api_request(
        Endpoints.FINANCIAL_HEALTH,
        params={"performanceId": performanceId},
    )
