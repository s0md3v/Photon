import random
import time

import requests
from requests.exceptions import TooManyRedirects


SESSION = requests.Session()
SESSION.max_redirects = 3

def requester(
        url,
        main_url=None,
        delay=0,
        cook=None,
        headers=None,
        timeout=10,
        host=None,
        proxies=[None],
        user_agents=[None],
        failed=None,
        processed=None
    ):
    """Handle the requests and return the response body."""
    cook = cook or set()
    headers = headers or set()
    user_agents = user_agents or ['Photon']
    failed = failed or set()
    processed = processed or set()
    # Mark the URL as crawled
    processed.add(url)
    # Pause/sleep the program for specified time
    time.sleep(delay)

    def make_request(url):
        """Default request"""
        final_headers = headers or {
            'Host': host,
            # Selecting a random user-agent
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'DNT': '1',
            'Connection': 'close',
        }
        try:
            response = SESSION.get(
                url,
                cookies=cook,
                headers=final_headers,
                verify=False,
                timeout=timeout,
                stream=True,
                proxies=random.choice(proxies)
            )
        except TooManyRedirects:
            return 'dummy'

        if 'text/html' in response.headers['content-type'] or \
           'text/plain' in response.headers['content-type']:
            if response.status_code != '404':
                return response.text
            else:
                response.close()
                failed.add(url)
                return 'dummy'
        else:
            response.close()
            return 'dummy'

    return make_request(url)
