import re

from core.scraper import scraper
from core.requester import requester
from core.load_modules import load_modules
from core.values import var, config, result
from core.utils import in_scope, handle_anchor, isHTML, get_domain

def parser(url):
    response = requester(url)
    if response:
        response_url = response.url
        response_page = response.text
        load_modules('while-parsing', response=response)
        if response_page:
            hrefs = [re.sub(r'^[\'"]|[\'"]$', '', match.group(1)) for match in re.finditer(r'(?i)<a[^>]+href=("[^"]+?"|\'[^\']+?\'|[^\s]+?)', response_page)]
            for href in hrefs:
                if re.search(r'(?i)^(#|javascript:)', href):
                    continue
                url = handle_anchor(response_url, href)
                if var['include']:
                    if not re.match(var['include'], url):
                        continue
                elif var['exclude']:
                    if re.match(var['exclude'], url):
                        continue
                this_domain = get_domain(url)
                for website in config['websites']:
                    if website in this_domain:
                        result['data']['websites'].add(url)
                        break
                html, extension = isHTML(url)
                if not html:
                    if extension.lower().startswith(tuple(config['files'])):
                        result['data']['files'].add(url)
                if in_scope(url):
                    if '=' in url:
                        result['urls']['fuzzable'].add(url)
                    result['urls']['internal'].add(url)
                else:
                    result['urls']['external'].add(url)
            scraper(response)
