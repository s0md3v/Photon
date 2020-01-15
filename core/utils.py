import re
import tld
import math
import json
import random
import requests

from fonetic import count
from urllib.parse import urlparse

from core.values import var
from core.colors import bad, info

def isHTML(url):
    document = re.search(r'/[^/?]+\.([^/?]+)(?:\?|$)', url)
    if document:
        extension = document.group(1)
        if not re.match(r'(?i)^(html|php|asp|phtml|xml|php)[^\.]*?$', extension):
            return (False, extension)
        return (True, extension)
    else:
        return (True, '')

def verbose(cat, data):
    if var['verbose']:
        print(info + ' ' + cat + ' ' + data)

def remove_regex(urls, regex):
    """
    Parse a list for non-matches to a regex.

    Args:
        urls: iterable of urls
        regex: string regex to be parsed for

    Returns:
        list of strings not matching regex
    """

    if not regex:
        return urls

    # To avoid iterating over the characters of a string
    if not isinstance(urls, (list, set, tuple)):
        urls = [urls]

    try:
        non_matching_urls = [url for url in urls if not re.search(regex, url)]
    except TypeError:
        return []

    return non_matching_urls

def writer(obj, path):
    kind = str(type(obj)).split('\'')[1]
    if kind == 'list' or kind == 'tuple':
        obj = '\n'.join(obj)
    elif kind == 'dict':
        obj = json.dumps(obj, indent=4)
    savefile = open(path, 'w+')
    savefile.write(str(obj.encode('utf-8').decode('utf-8')))
    savefile.close()

def reader(path, string=False):
    with open(path, 'r') as f:
        result = [line.rstrip('\n').encode('utf-8').decode('utf-8') for line in f]
    if string:
        return '\n'.join(result)
    else:
        return result


def timer(diff, processed):
    """Return the passed time."""
    # Changes seconds into minutes and seconds
    minutes, seconds = divmod(diff, 60)
    if processed:
        try:
            # Finds average time taken by requests
            requests_per_second = float(len(processed)/seconds)
        except:
            requests_per_second = 0
        return minutes, seconds, requests_per_second
    else:
        return minutes, seconds, 0


def is_token(string):
    if string.isdigit():
        return True
    total, good, bad = count(string)
    if total:
        bad_percentage = (bad * 100)/total
        if total >= 5:
            if bad_percentage > 40:
                return True
            else:
                False
        else:
            return True
    return False


def entropy(string):
    """Calculate the entropy of a string."""
    entropy = 0
    for number in range(256):
        result = float(string.count(
            chr(number))) / len(string)
        if result != 0:
            entropy = entropy - result * math.log(result, 2)
    return entropy


def raw_urls(response):
    # Regex for extracting URLs
    return re.findall(r'https?://[^$\'"`\s\r\n]+', response)


def log(kind, string):
    """Enable verbose output."""
    if var['verbose']:
        print('%s %s: %s' % (info, kind, string))


def extract_headers(headers):
    """This function extracts valid headers from interactive input."""
    sorted_headers = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers


def get_tld(url, fix_protocol=True):
    """Extract the top level domain from an URL."""
    ext = tld.get_tld(url, fix_protocol=fix_protocol)
    toplevel = '.'.join(urlparse(url).netloc.split('.')[-2:]).split(ext)[0] + ext
    return toplevel

def get_domain(url):
    """Extract the domain from an URL."""
    return urlparse(url).netloc

def stabilize(url):
    "picks up the best suiting protocol if not present already"
    if 'http' not in url:
        try:
            requests.get('https://%s' % url) # Makes request to the target with http scheme
            url = 'https://%s' % url
        except: # if it fails, maybe the target uses https scheme
            url = 'http://%s' % url

    try:
        requests.get(url) # Makes request to the target
    except Exception as e: # if it fails, the target is unreachable
        if 'ssl' in str(e).lower():
            pass
        else:
            print ('%s Unable to connect to the target.' % bad)
            quit()
    return url

def seperator(response):
    html = '\n'.join(re.findall(r'<[a-zA-z][^>]*?>', response))
    js = '\n'.join([i.group(1) for i in re.finditer(r'(?m)<script[^>]*?>([.\s\S]+?)</script>', response)])
    text = re.sub(r'<(script|style)[^>]*?>[\s\S]*?</(script|style)>|<[a-zA-Z][^>]*?>|<!--[\s\S]*?-->|</[a-zA-Z][^>]*?>', '', response)
    return js, text, html

def in_scope(url):
    if var['wide']:
        if get_tld(url) == var['scope']:
            return True
    else:
        if get_domain(url) == var['scope']:
            return True
    return False

def get_agent():
    if var['random_agent']:
        return random.choice(var['user_agents'])
    elif var['as_google']:
        return 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    else:
        return 'Photon (https://github.com/s0md3v/Photon)'

def handle_anchor(parent, child):
    parsed_parent = urlparse(parent)
    parsed_child = urlparse(child)
    if parsed_child.scheme:
        return child
    elif (parsed_child.path).startswith('//'):
        return parsed_child.scheme + ':' + child
    clean = re.sub(r'https?://' + parsed_parent.netloc, '', parent)
    without_file = '/'.join(clean.split('/')[:-1])
    if re.search(r'^(?:/?\.\./)+', child):
        dots = len(re.findall(r'^(?:/?\.\./)+', child))
        go_up = ''
        if without_file:
            go_up = '/'.join(without_file.rstrip('/').split('/')[:-dots])
        child = re.sub(r'^(?:/?\.\./)+', '', child).rstrip('/')
        return parsed_parent.scheme + '://' + parsed_parent.netloc + go_up + '/' + child
    else:
        return parsed_parent.scheme + '://' + parsed_parent.netloc + without_file + '/' + child.lstrip('/')

def deJSON(data):
    return data.replace('\\\\', '\\')
