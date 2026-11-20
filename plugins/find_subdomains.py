"""Support for viewdns.info"""
from re import findall

from requests import get


def find_subdomains(domain):
    """Find subdomains according to the TLD."""
    result = set()
    response = get('https://viewdns.info/subdomains/?domain=' + domain).text
    matches = findall(r'"name": "(.*?)",\n', response)
    for match in matches:
        result.add(match.replace(' ', '').replace('\n', ''))
    return list(result)
