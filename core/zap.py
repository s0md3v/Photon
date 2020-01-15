import re

from core.colors import good
from core.values import var, result
from core.requester import requester
from core.utils import log, handle_anchor, raw_urls


def zap():
    root_url = var['root_url']
    # Makes request to robots.txt
    response = requester(root_url + '/robots.txt', crawl=False)
    # Making sure robots.txt isn't some fancy 404 page
    if response and '<body' not in response.text:
        # If you know it, you know it
        disallowed_list = re.search(r'User-agent: \*[.\s\S]*?(?:Sitemap:|User-agent:|$)', response.text)
        if disallowed_list:
            matches = re.finditer(r'(?m)^Disallow:\s+(.*?)$', disallowed_list.group(0))
            for match in matches:
                match = match.group(1)
                if match != '/':
                    url = root_url + match.replace('?', '\?').replace('*', '[^/]*?')
                    # Add the URL to robots list
                    result['urls']['disallowed'].add(url)
    result['urls']['disallowed'] = list(result['urls']['disallowed'])
    if result['urls']['disallowed']:
        print('^' + '|^'.join(result['urls']['disallowed']))
        var['exclude'] = re.compile('^' + '|^'.join(result['urls']['disallowed']))
    sitemaps = set([root_url + '/sitemap.xml'])
    matches =  re.finditer(r'Sitemap: (.*?)$', response.text)
    if matches:
        for match in matches:
            sitemaps.append(handle_anchor(root_url, match.group(1)))
    for sitemap in sitemaps:
        response = requester(sitemap, crawl=False)
        # Making sure it isn't some fancy 404 page
        if response and '<body' not in response.text:
            matches = raw_urls(response.text)
            if matches: # if there are any matches
                print('%s URLs retrieved from %s: %i' % (
                    good, sitemap, len(matches)))
                for match in matches:
                    log('Internal page', match)
                    # Cleaning up the URL and adding it to the internal list for
                    # crawling
                    result['urls']['internal'].add(match)
