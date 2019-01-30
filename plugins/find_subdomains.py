"""Support for findsubdomains.com."""
from re import findall

from requests import get


def find_subdomains(domain):
    """Find subdomains according to the TLD."""
    result = set()
    response = get('https://findsubdomains.com/subdomains-of/' + domain).text
    matches = findall(r'(?s)<div class="domains js-domain-name">(.*?)</div>', response)
    for match in matches:
        result.add(match.replace(' ', '').replace('\n', ''))
    return list(result)
