from datetime import datetime
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from random import randrange
import time

from NBAScrapper.src.services import GameService
from NBAScrapper.src.utils import Log

MIN_BS4_WAITING_TIME = 9  # Seconds
MAX_BS4_WAITING_TIME = 13  # Seconds
RECONNECTION_WAITING_TIME = 60  # Seconds
RECONNECTION_MANY_REQUEST_TIME = 3660  # Seconds
RECONNECTION_ATTEMPTS = 24  # Tries

HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,image/apng,*/*;q=0.8"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
    {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7"}
]

# Proxies not allowed in HTTPS in Python3
PROXIES = []


def init_bs4(url: str) -> BeautifulSoup | None:
    """Open the URL given before a little waiting time"""
    bs4_waiting_time()

    # urllib.error.HTTPError: HTTP Error 520:
    response = None
    attempts = 0
    while response is None:
        try:
            response = urlopen(Request(url=url, headers=get_random_header()))
        except (HTTPError, URLError) as error:
            Log.log_error("connection_error", str(error) + "\n\tURL: " + url)
            if error.code == 404:
                if "boxscores" in url:
                    game_id = url[-17:-5]
                    game_exist = GameService.check_game_exist(game_id)
                    if game_exist:
                        return None
                    else:
                        GameService.delete_game(game_id)
                else:
                    return None
            elif attempts < RECONNECTION_ATTEMPTS:
                attempts += 1
                if error.code == 429:
                    reconnection_many_request()
                else:
                    reconnection_waiting_time()
                pass
            else:
                raise

    html = response.read()
    return BeautifulSoup(html, 'html.parser')


def test_bs4(url: str) -> BeautifulSoup:
    """Open the URL given before a little waiting time"""
    bs4_waiting_time()

    # urllib.error.HTTPError: HTTP Error 520:
    response = None
    while response is None:
        try:
            response = urlopen(Request(url=url, headers=get_random_header()))
        except (HTTPError, URLError) as error:
            Log.log_error("test", str(error) + "\n\tURL: " + url)
            reconnection_waiting_time()
            pass

    html = response.read()
    return BeautifulSoup(html, 'html.parser')


def get_random_header() -> dict[str, str]:
    """Get a random header establish"""
    header = HEADERS[randrange(len(HEADERS))]
    return header


def get_random_proxy() -> str:
    """Get a random proxy establish"""
    proxy = PROXIES[randrange(len(PROXIES))]
    return proxy


def bs4_waiting_time():
    """Set a waiting time between the minimum and maximum time in beautiful soup calls"""
    time.sleep(randrange(MIN_BS4_WAITING_TIME, MAX_BS4_WAITING_TIME))


def wait_next_day():
    """The information is updated at 10:37, then wait until 11:00"""
    time_to_update = datetime.now()
    time_to_update = time_to_update.replace(hour=11, minute=0)

    now = datetime.now()

    dif_time = time_to_update - now
    time.sleep(dif_time.seconds)


def reconnection_waiting_time():
    """Set a waiting time to reconnect with the web page"""
    time.sleep(RECONNECTION_WAITING_TIME)


def reconnection_many_request():
    """Set a waiting time to reconnect with the web page"""
    time.sleep(RECONNECTION_MANY_REQUEST_TIME)


def is_full_check() -> bool:
    """Return if we have to check all team information
    Check all team information each Monday"""
    now = datetime.now()
    if now.weekday() == 0:
        return True
    else:
        return False


def is_full_player_check() -> bool:
    """Return if we have to check all team information
    Check all team information each first of the month"""
    now = datetime.now()
    if now.day == 1:
        return True
    else:
        return False
