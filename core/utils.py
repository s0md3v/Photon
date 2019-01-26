import re
import tld
import math
from core.config import verbose, badTypes
from core.colors import info

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

supress_regex = False

def regxy(pattern, response, custom):
    """Extract a string based on regex pattern supplied by user."""
    try:
        matches = re.findall(r'%s' % pattern, response)
        for match in matches:
            verb('Custom regex', match)
            custom.add(match)
    except:
        supress_regex = True


def is_link(url, processed, files):
    """Check whether an URL should be crawled or not."""
    # File extension that don't need to be crawled and are files
    # Whether the the url should be crawled or not
    conclusion = False
    # If the URL hasn't been crawled already
    if url not in processed:
        if url.split('.')[-1].lower() in badTypes:
            files.add(url)
        else:
            return True
    return conclusion


def remove_regex(urls, regex):
    """
    Parse a list for non-matches to a regex.

    Args:
        urls: iterable of urls
        custom_regex: string regex to be parsed for

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

def writer(datasets, dataset_names, output_dir):
    """Write the results."""
    for dataset, dataset_name in zip(datasets, dataset_names):
        if dataset:
            filepath = output_dir + '/' + dataset_name + '.txt'
            with open(filepath, 'w+') as out_file:
                joined = '\n'.join(dataset)
                out_file.write(str(joined.encode('utf-8')))
                out_file.write('\n')

def timer(diff, processed):
    """Return the passed time."""
    # Changes seconds into minutes and seconds
    minutes, seconds = divmod(diff, 60)
    try:
        # Finds average time taken by requests
        time_per_request = diff / float(len(processed))
    except ZeroDivisionError:
        time_per_request = 0
    return minutes, seconds, time_per_request

def entropy(string):
    """Calculate the entropy of a string."""
    entropy = 0
    for number in range(256):
        result = float(string.encode('utf-8').count(
            chr(number)))/len(string.encode('utf-8'))
        if result != 0:
            entropy = entropy - result * math.log(result, 2)
    return entropy

def xmlParser(response):
    """Extract links from .xml files."""
    # Regex for extracting URLs
    return re.findall(r'<loc>(.*?)</loc>', response)

def verb(kind, string):
    """Enable verbose output."""
    if verbose:
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

def top_level(url):
    """Extract the top level domain from an URL."""
    ext = tld.get_tld(url, fix_protocol=True)
    toplevel = '.'.join(urlparse(url).netloc.split('.')[-2:]).split(
        ext)[0] + ext
    return toplevel
