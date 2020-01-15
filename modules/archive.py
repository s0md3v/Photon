import json
import requests

from core.values import var, result
from core.utils import isHTML

meta = {
	'author' : 'Somdev Sangwan',
	'description' : 'fetches seeds fom archive.org',
	'phase' : 'before-crawling'
}

def archive(data):
    host = var['scope']
    if var['wide']:
        mode = 'host'
    else:
        mode = 'domain'
    url = '''http://web.archive.org/cdx/search?url=%s&matchType=%s&collapse=urlkey&fl=original
    &filter=mimetype:text/html&filter=statuscode:200&output=json''' % (host, mode)
    response = requests.get(url).text
    parsed = json.loads(response)[1:]
    for item in parsed:
        url = item[0]
        if isHTML(url):
            result['urls']['internal'].add(url)
