"""Support for archive.org."""
import json

from requests import get


def time_machine(host, mode):
    """Query archive.org."""
    url = "http://web.archive.org/cdx/search?url=%s&matchType=%s&collapse=urlkey&fl=original&filter=mimetype:text/html&filter=statuscode:200&output=json&from=20180101&to=20181231" % (host, mode)
    response = get(url).text
    parsed = json.loads(response)[1:]
    urls = []
    for item in parsed:
        urls.append(item[0])
    return urls
