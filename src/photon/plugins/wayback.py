"""Support for archive.org."""
import datetime
import json

from requests import get


def time_machine(host, mode):
    """Query archive.org."""
    now = datetime.datetime.now()
    to = str(now.year) + str(now.day) + str(now.month)
    if now.month > 6:
    	fro = str(now.year) + str(now.day) + str(now.month - 6)
    else:
    	fro = str(now.year - 1) + str(now.day) + str(now.month + 6)
    url = "http://web.archive.org/cdx/search?url=%s&matchType=%s&collapse=urlkey&fl=original&filter=mimetype:text/html&filter=statuscode:200&output=json&from=%s&to=%s" % (host, mode, fro, to)
    response = get(url).text
    parsed = json.loads(response)[1:]
    urls = []
    for item in parsed:
        urls.append(item[0])
    return urls
