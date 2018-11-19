"""Support for archive.org."""
import json

from requests import get


def timeMachine(host, mode):
    """Query archive.org."""
    url = "http://web.archive.org/cdx/search/cdx?url=%s&matchType=host&collapse=urlkey&filter=statuscode:200&output=json" % host
    response = get(url).text
    parsed = json.loads(response)[1:]
    urls = []
    for item in parsed:
        urls.append(item[2])
    return urls
