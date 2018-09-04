from re import findall
from requests import get

def findSubdomains(domain):
    result = set()
    response = get('https://findsubdomains.com/subdomains-of/' + domain).text
    parts = response.split('data-row')
    for part in parts:
        matches = findall(r'rel="nofollow" href="([^/]*)" target="_blank"', part)
        for match in matches:
            result.add(match)
    return list(result)