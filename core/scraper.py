import re

from core.values import config, result
from core.load_modules import load_modules
from core.utils import seperator, deJSON, verbose


def scraper(response):
    matches = {}
    js, text, html = seperator(response.text)
    load_modules('while-scraping', response=response.text, js=js, text=text, html=html)
    for pattern in config['extractors']:
        if config['extractors'][pattern]['enabled']:
            regex =  deJSON(config['extractors'][pattern]['regex'])
            location =  config['extractors'][pattern]['location']
            if location == 'any':
                for match in re.finditer(regex, response.text):
                    verbose('Extractor:', regex + ' => ' + match.group(1))
                    matches[match.group(1)] = pattern
            elif location == 'js':
                for match in re.finditer(regex, js):
                    verbose('Extractor:', regex + ' => ' + match.group(1))
                    matches[match.group(1)] = pattern
            elif location == 'text':
                for match in re.finditer(regex, text):
                    verbose('Extractor:', regex + ' => ' + match.group(1))
                    matches[match.group(1)] = pattern
            elif location == 'html':
                for match in re.finditer(regex, html):
                    verbose('Extractor:', regex + ' => ' + match.group(1))
                    matches[match.group(1)] = pattern
    for match, pattern in matches.items():
        if pattern not in result['data']['extractors']:
            result['data']['extractors'][pattern] = {}
        if match not in result['data']['extractors'][pattern]:
            result['data']['extractors'][pattern][match] = response.url
