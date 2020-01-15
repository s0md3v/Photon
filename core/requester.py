import time
import requests

from urllib.parse import urlparse
from requests.exceptions import TooManyRedirects, ReadTimeout, ConnectionError

from core.values import var, result
from core.utils import get_agent, verbose
from core.load_modules import load_modules

session = requests.Session()
session.max_redirects = 3
requests.max_retries = 1

def requester(url, crawl=True):
    """Handle the requests and return the response body."""
    headers = var['headers'] or {
        'Host': urlparse(url).netloc,
        # Selecting a random user-agent
        'User-Agent': get_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'DNT': '1',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1'
    }

    # Mark the URL as crawled
    var['processed'].add(url)
    # Pause/sleep the program for specified time
    time.sleep(var['delay'])
    try:
        response = session.get(
            url,
            stream=True,
            verify=False,
            headers=headers,
            cookies=var['cookie'],
            timeout=var['timeout'],
        )
        verbose('Response:', response.url + ':' + str(response.status_code))
    except (TooManyRedirects, ConnectionError, ConnectionRefusedError, ReadTimeout):
        result['urls']['failed'].add(url)
        return False
    if crawl:
        load_modules('after-response', response=response)
        verbose('Response:', response.url + ':' + str(response.status_code))
        if 'content-type' in response.headers:
            if ('text/html' or 'text/plain' or 'application/json' or 'xml') in response.headers['content-type']:
                if response.status_code != '404':
                    return response
                else:
                    response.close()
                    result['urls']['failed'].add(url)
                    return False
        else:
            return response
    else:
        return response
