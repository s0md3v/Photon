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
        ninja=False,
        user_agents=None,
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

    def normal(url):
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
                stream=True
            )
        except TooManyRedirects:
            return 'dummy'
        if 'text/html' in response.headers['content-type']:
            if response.status_code != '404':
                return response.text
            else:
                response.close()
                failed.add(url)
                return 'dummy'
        else:
            response.close()
            return 'dummy'

    def facebook(url):
        """Interact with the developer.facebook.com API."""
        return requests.get(
            'https://developers.facebook.com/tools/debug/echo/?q=' + url,
            verify=False
        ).text

    def pixlr(url):
        """Interact with the pixlr.com API."""
        if url == main_url:
            # Because pixlr throws error if http://example.com is used
            url = main_url + '/'
        return requests.get(
            'https://pixlr.com/proxy/?url=' + url,
            headers={'Accept-Encoding': 'gzip'},
            verify=False
        ).text

    def code_beautify(url):
        """Interact with the codebeautify.org API."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://codebeautify.org',
            'Connection': 'close',
        }
        return requests.post(
            'https://codebeautify.com/URLService',
            headers=headers,
            data='path=' + url,
            verify=False
        ).text

    def photopea(url):
        """Interact with the www.photopea.com API."""
        return requests.get(
            'https://www.photopea.com/mirror.php?url=' + url, verify=False).text

    if ninja:  # If the ninja mode is enabled
        # Select a random request function i.e. random API
        response = random.choice(
            [photopea, normal, facebook, pixlr, code_beautify])(url)
        return response or 'dummy'
    else:
        return normal(url)
