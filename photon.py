#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Photon main part."""
from __future__ import print_function

import argparse
import os
import random
import sys
import threading
import time
import warnings
from math import log
from re import findall, search

from requests import get, post

import tld
from core.config import badTypes, intels
from core.prompt import prompt

try:
    import concurrent.futures
    from urllib.parse import urlparse  # For Python 3
    python2, python3 = False, True
except ImportError:
    from urlparse import urlparse  # For Python 2
    python2, python3 = True, False


try:
    input = raw_input
except NameError:
    pass

# Output should be colored
colors = True
# Detecting the OS of current system
machine = sys.platform
if machine.lower().startswith(('os', 'win', 'darwin', 'ios')):
    # Colors shouldn't be displayed on macOS and Windows
    colors = False
if not colors:
    end = red = white = green = yellow = run = bad = good = info = que = ''
else:
    end = '\033[1;m'
    red = '\033[91m'
    white = '\033[1;97m'
    green = '\033[1;32m'
    yellow = '\033[1;33m'
    run = '\033[1;97m[~]\033[1;m'
    bad = '\033[1;31m[-]\033[1;m'
    good = '\033[1;32m[+]\033[1;m'
    info = '\033[1;33m[!]\033[1;m'
    que = '\033[1;34m[?]\033[1;m'

# Just a fancy ass banner
print('''%s      ____  __          __
     / %s__%s \/ /_  ____  / /_____  ____
    / %s/_/%s / __ \/ %s__%s \/ __/ %s__%s \/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\____/\__/\____/_/ /_/ %sv1.1.5%s\n''' %
      (red, white, red, white, red, white, red, white, red, white, red, white,
       red, white, end))

# Disable SSL related warnings
warnings.filterwarnings('ignore')

# Processing command line arguments
parser = argparse.ArgumentParser()
# Options
parser.add_argument('-u', '--url', help='root url', dest='root')
parser.add_argument('-c', '--cookie', help='cookie', dest='cook')
parser.add_argument('-r', '--regex', help='regex pattern', dest='regex')
parser.add_argument('-e', '--export', help='export format', dest='export')
parser.add_argument('-o', '--output', help='output directory', dest='output')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level',
                    type=int)
parser.add_argument('-t', '--threads', help='number of threads', dest='threads',
                    type=int)
parser.add_argument('-d', '--delay', help='delay between requests',
                    dest='delay', type=float)
parser.add_argument('-v', '--verbose', help='verbose output', dest='verbose',
                    action='store_true')
parser.add_argument('-s', '--seeds', help='additional seed URLs', dest='seeds',
                    nargs="+", default=[])
parser.add_argument('--stdout', help='send variables to stdout', dest='std')
parser.add_argument('--user-agent', help='custom user agent(s)',
                    dest='user_agent')
parser.add_argument('--exclude', help='exclude URLs matching this regex',
                    dest='exclude')
parser.add_argument('--timeout', help='http request timeout', dest='timeout',
                    type=float)

# Switches
parser.add_argument('--headers', help='add headers', dest='headers',
                    action='store_true')
parser.add_argument('--dns', help='enumerate subdomains and DNS data',
                    dest='dns', action='store_true')
parser.add_argument('--ninja', help='ninja mode', dest='ninja',
                    action='store_true')
parser.add_argument('--keys', help='find secret keys', dest='api',
                    action='store_true')
parser.add_argument('--update', help='update photon', dest='update',
                    action='store_true')
parser.add_argument('--only-urls', help='only extract URLs', dest='only_urls',
                    action='store_true')
parser.add_argument('--wayback', help='fetch URLs from archive.org as seeds',
                    dest='archive', action='store_true')
args = parser.parse_args()


def update():
    """Update the current installation.

    git clones the latest version and merges it with the current directory.
    """
    print('%s Checking for updates' % run)
    # Changes must be separated by ;
    changes = "--headers option for interactive HTTP header input"
    latest_commit = get('https://raw.githubusercontent.com/s0md3v/Photon/master/photon.py').text
    # Just a hack to see if a new version is available
    if changes not in latest_commit:
        changelog = search(r"changes = '''(.*?)'''", latest_commit)
        # Splitting the changes to form a list
        changelog = changelog.group(1).split(';')
        print('%s A new version of Photon is available.' % good)
        print('%s Changes:' % info)
        for change in changelog: # print changes
            print('%s>%s %s' % (green, end, change))

        current_path = os.getcwd().split('/') # if you know it, you know it
        folder = current_path[-1] # current directory name
        path = '/'.join(current_path) # current directory path
        choice = input('%s Would you like to update? [Y/n] ' % que).lower()

        if choice != 'n':
            print('%s Updating Photon' % run)
            os.system('git clone --quiet https://github.com/s0md3v/Photon %s'
                      % (folder))
            os.system('cp -r %s/%s/* %s && rm -r %s/%s/ 2>/dev/null'
                      % (path, folder, path, path, folder))
            print('%s Update successful!' % good)
    else:
        print('%s Photon is up to date!' % good)


# If the user has supplied --update argument
if args.update:
    update()
    quit()

# If the user has supplied a URL
if args.root:
    main_inp = args.root
    if main_inp.endswith('/'):
        # We will remove it as it can cause problems later in the code
        main_inp = main_inp[:-1]
# If the user hasn't supplied an URL
else:
    print('\n' + parser.format_help().lower())
    quit()

headers = args.headers  # prompt for headers
verbose = args.verbose  # verbose output
delay = args.delay or 0  # Delay between requests
timeout = args.timeout or 6  # HTTP request timeout
cook = args.cook or None  # Cookie
api = bool(args.api)  # Extract high entropy strings i.e. API keys and stuff
ninja = bool(args.ninja)  # Ninja mode toggle
crawl_level = args.level or 2  # Crawling level
thread_count = args.threads or 2  # Number of threads
only_urls = bool(args.only_urls)  # Only URLs mode is off by default

# Variables we are gonna use later to store stuff
keys = set()  # High entropy strings, prolly secret keys
files = set()  # The pdf, css, png, etc files.
intel = set()  # The email addresses, website accounts, AWS buckets etc.
robots = set()  # The entries of robots.txt
custom = set()  # Strings extracted by custom regex pattern
failed = set()  # URLs that photon failed to crawl
scripts = set()  # THe Javascript files
external = set()  # URLs that don't belong to the target i.e. out-of-scope
# URLs that have get params in them e.g. example.com/page.php?id=2
fuzzable = set()
endpoints = set()  # URLs found from javascript files
processed = set()  # URLs that have been crawled
# URLs that belong to the target i.e. in-scope
internal = set([s for s in args.seeds])

everything = []
bad_intel = set()  # Unclean intel urls
bad_scripts = set()  # Unclean javascript file urls


def extract_headers(headers):
    """This function extracts valid headers from interactive input."""
    sorted_headers = {}
    matches = findall(r'(.*):\s(.*)', headers)
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


if headers:
    headers = extract_headers(prompt())

# If the user hasn't supplied the root URL with http(s), we will handle it
if main_inp.startswith('http'):
    main_url = main_inp
else:
    try:
        get('https://' + main_inp)
        main_url = 'https://' + main_inp
    except:
        main_url = 'http://' + main_inp

schema = main_url.split('//')[0] # https: or http:?
# Adding the root URL to internal for crawling
internal.add(main_url)
# Extracts host out of the URL
host = urlparse(main_url).netloc

output_dir = args.output or host


def top_level(url):
    """Extract the top level domain from an URL."""
    ext = tld.get_tld(host, fix_protocol=True)
    toplevel = '.'.join(urlparse(main_url).netloc.split('.')[-2:]).split(
        ext)[0] + ext
    return toplevel

try:
    domain = top_level(main_url)
except:
    domain = host

if args.user_agent:
    user_agents = args.user_agent.split(',')
else:
    with open(sys.path[0] + '/core/user-agents.txt', 'r') as uas:
        user_agents = [agent.strip('\n') for agent in uas]


def requester(url):
    """Handle the requests and return the response body."""
    # Mark the URL as crawled
    processed.add(url)
    # Pause/sleep the program for specified time
    time.sleep(delay)

    def normal(url):
        """Default request"""
        finalHeaders = headers or {
            'Host': host,
            # Selecting a random user-agent
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'DNT': '1',
            'Connection': 'close',
        }
        response = get(url, cookies=cook, headers=finalHeaders, verify=False,
                       timeout=timeout, stream=True)
        if 'text/html' in response.headers['content-type']:
            if response.status_code != '404':
                return response.text
            else:
                response.close()
                failed.add(url)
                return 'dummy'
        else:
            response.close()
            return 'dummy'

    def facebook(url):
        """Interact with the developer.facebook.com API."""
        return get('https://developers.facebook.com/tools/debug/echo/?q=' + url,
                   verify=False).text

    def pixlr(url):
        """Interact with the pixlr.com API."""
        if url == main_url:
            # Because pixlr throws error if http://example.com is used
            url = main_url + '/'
        return get('https://pixlr.com/proxy/?url=' + url,
                   headers={'Accept-Encoding' : 'gzip'}, verify=False).text

    def code_beautify(url):
        """Interact with the codebeautify.org API."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://codebeautify.org',
            'Connection': 'close',
        }
        return post('https://codebeautify.com/URLService', headers=headers,
                    data='path=' + url, verify=False).text

    def photopea(url):
        """Interact with the www.photopea.com API."""
        return get(
            'https://www.photopea.com/mirror.php?url=' + url, verify=False).text

    if ninja:  # If the ninja mode is enabled
        # Select a random request function i.e. random API
        response = random.choice(
            [photopea, normal, facebook, pixlr, code_beautify])(url)
        return response or 'dummy'
    else:
        return normal(url)


def verb(kind, string):
    """Enable verbose output."""
    if verbose:
        print('%s %s: %s' % (info, kind, string))


def xmlParser(response):
    """Extract links from .xml files."""
    # Regex for extracting URLs
    return findall(r'<loc>(.*?)</loc>', response)


def zap(url):
    """Extract links from robots.txt and sitemap.xml."""
    if args.archive:
        from plugins.wayback import time_machine
        print('%s Fetching URLs from archive.org' % run)
        if False:
            archived_urls = time_machine(domain, 'domain')
        else:
            archived_urls = time_machine(host, 'host')
        print('%s Retrieved %i URLs from archive.org' % (
            good, len(archived_urls) - 1))
        for url in archived_urls:
            verb('Internal page', url)
            internal.add(url)
    # Makes request to robots.txt
    response = get(url + '/robots.txt', verify=False).text
    # Making sure robots.txt isn't some fancy 404 page
    if '<body' not in response:
        # If you know it, you know it
        matches = findall(r'Allow: (.*)|Disallow: (.*)', response)
        if matches:
            # Iterating over the matches, match is a tuple here
            for match in matches:
                # One item in match will always be empty so will combine both
                # items
                match = ''.join(match)
                # If the URL doesn't use a wildcard
                if '*' not in match:
                    url = main_url + match
                    # Add the URL to internal list for crawling
                    internal.add(url)
                    # Add the URL to robots list
                    robots.add(url)
            print('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
    # Makes request to sitemap.xml
    response = get(url + '/sitemap.xml', verify=False).text
    # Making sure robots.txt isn't some fancy 404 page
    if '<body' not in response:
        matches = xmlParser(response)
        if matches: # if there are any matches
            print('%s URLs retrieved from sitemap.xml: %s' % (
                good, len(matches)))
            for match in matches:
                verb('Internal page', url)
                # Cleaning up the URL and adding it to the internal list for
                # crawling
                internal.add(match)


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
        non_matching_urls = [url for url in urls if not search(regex, url)]
    except TypeError:
        return []

    return non_matching_urls


def is_link(url):
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


supress_regex = False


def regxy(pattern, response):
    """Extract a string based on regex pattern supplied by user."""
    try:
        matches = findall(r'%s' % pattern, response)
        for match in matches:
            verb('Custom regex', match)
            custom.add(match)
    except:
        supress_regex = True


def intel_extractor(response):
    """Extract intel from the response body."""
    matches = findall(r'([\w\.-]+s[\w\.-]+\.amazonaws\.com)|([\w\.-]+@[\w\.-]+\.[\.\w]+)', response)
    if matches:
        for match in matches:
            verb('Intel', match)
            bad_intel.add(match)


def js_extractor(response):
    """Extract js files from the response body"""
    # Extract .js files
    matches = findall(r'<(script|SCRIPT).*(src|SRC)=([^\s>]+)', response)
    for match in matches:
        match = match[2].replace('\'', '').replace('"', '')
        verb('JS file', match)
        bad_scripts.add(match)


def entropy(payload):
    """Calculate the entropy of a string."""
    entropy = 0
    for number in range(256):
        result = float(payload.encode('utf-8').count(
            chr(number)))/len(payload.encode('utf-8'))
        if result != 0:
            entropy = entropy - result * log(result, 2)
    return entropy


def extractor(url):
    """Extract details from the response body."""
    response = requester(url)
    matches = findall(r'<[aA].*(href|HREF)=([^\s>]+)', response)
    for link in matches:
        # Remove everything after a "#" to deal with in-page anchors
        link = link[1].replace('\'', '').replace('"', '').split('#')[0]
        # Checks if the URLs should be crawled
        if is_link(link):
            if link[:4] == 'http':
                if link.startswith(main_url):
                    verb('Internal page', link)
                    internal.add(link)
                else:
                    verb('External page', link)
                    external.add(link)
            elif link[:2] == '//':
                if link.split('/')[2].startswith(host):
                    verb('Internal page', link)
                    internal.add(schema + link)
                else:
                    verb('External page', link)
                    external.add(link)
            elif link[:1] == '/':
                verb('Internal page', link)
                internal.add(main_url + link)
            else:
                verb('Internal page', link)
                internal.add(main_url + '/' + link)

    if not only_urls:
        intel_extractor(response)
        js_extractor(response)
    if args.regex and not supress_regex:
        regxy(args.regex, response)
    if api:
        matches = findall(r'[\w-]{16,45}', response)
        for match in matches:
            if entropy(match) >= 4:
                verb('Key', match)
                keys.add(url + ': ' + match)


def jscanner(url):
    """Extract endpoints from JavaScript code."""
    response = requester(url)
    # Extract URLs/endpoints
    matches = findall(r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]', response)
    # Iterate over the matches, match is a tuple
    for match in matches:
        # Combining the items because one of them is always empty
        match = match[0] + match[1]
        # Making sure it's not some JavaScript code
        if not search(r'[}{><"\']', match) and not match == '/':
            verb('JS endpoint', match)
            endpoints.add(match)


def threader(function, *urls):
    """Start multiple threads for a function."""
    threads = []
    # Because URLs is a tuple
    urls = urls[0]
    # Iterating over URLs
    for url in urls:
        task = threading.Thread(target=function, args=(url,))
        threads.append(task)
    # Start threads
    for thread in threads:
        thread.start()
    # Wait for all threads to complete their work
    for thread in threads:
        thread.join()
    # Delete threads
    del threads[:]


def flash(function, links):
    """Process the URLs and uses a threadpool to execute a function."""
    # Convert links (set) to list
    links = list(links)
    if sys.version_info < (3, 2):
        for begin in range(0, len(links), thread_count):  # Range with step
            end = begin + thread_count
            splitted = links[begin:end]
            threader(function, splitted)
            progress = end
            if progress > len(links):  # Fix if overflow
                progress = len(links)
            print('\r%s Progress: %i/%i' % (info, progress, len(links)),
                  end='\r')
            sys.stdout.flush()
    else:
        threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers=thread_count)
        futures = (threadpool.submit(function, link) for link in links)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(links) or (i + 1) % thread_count == 0:
                print('%s Progress: %i/%i' % (info, i + 1, len(links)),
                      end='\r')
    print('')

# Records the time at which crawling started
then = time.time()

# Step 1. Extract urls from robots.txt & sitemap.xml
zap(main_url)

# This is so the level 1 emails are parsed as well
internal = set(remove_regex(internal, args.exclude))

# Step 2. Crawl recursively to the limit specified in "crawl_level"
for level in range(crawl_level):
    # Links to crawl = (all links - already crawled links) - links not to crawl
    links = remove_regex(internal - processed, args.exclude)
    # If links to crawl are 0 i.e. all links have been crawled
    if not links:
        break
    # if crawled links are somehow more than all links. Possible? ;/
    elif len(internal) <= len(processed):
        if len(internal) > 2 + len(args.seeds):
            break
    print('%s Level %i: %i URLs' % (run, level + 1, len(links)))
    try:
        flash(extractor, links)
    except KeyboardInterrupt:
        print('')
        break

if not only_urls:
    for match in bad_scripts:
        if match.startswith(main_url):
            scripts.add(match)
        elif match.startswith('/') and not match.startswith('//'):
            scripts.add(main_url + match)
        elif not match.startswith('http') and not match.startswith('//'):
            scripts.add(main_url + '/' + match)
    # Step 3. Scan the JavaScript files for endpoints
    print('%s Crawling %i JavaScript files' % (run, len(scripts)))
    flash(jscanner, scripts)

    for url in internal:
        if '=' in url:
            fuzzable.add(url)

    for match in bad_intel:
        for x in match:  # Because "match" is a tuple
            if x != '':  # If the value isn't empty
                intel.add(x)
        for url in external:
            try:
                if tld.get_tld(url, fix_protocol=True) in intels:
                    intel.add(url)
            except:
                pass

# Records the time at which crawling stopped
now = time.time()
# Finds total time taken
diff = (now - then)


def timer(diff):
    """Return the passed time."""
    # Changes seconds into minutes and seconds
    minutes, seconds = divmod(diff, 60)
    try:
        # Finds average time taken by requests
        time_per_request = diff / float(len(processed))
    except ZeroDivisionError:
        time_per_request = 0
    return minutes, seconds, time_per_request
minutes, seconds, time_per_request = timer(diff)

# Step 4. Save the results
if not os.path.exists(output_dir): # if the directory doesn't exist
    os.mkdir(output_dir) # create a new directory

datasets = [files, intel, robots, custom, failed, internal, scripts,
            external, fuzzable, endpoints, keys]
dataset_names = ['files', 'intel', 'robots', 'custom', 'failed', 'internal',
                 'scripts', 'external', 'fuzzable', 'endpoints', 'keys']

def writer(datasets, dataset_names, output_dir):
    """Write the results."""
    for dataset, dataset_name in zip(datasets, dataset_names):
        if dataset:
            filepath = output_dir + '/' + dataset_name + '.txt'
            if python3:
                with open(filepath, 'w+', encoding='utf8') as out_file:
                    out_file.write(str('\n'.join(dataset)))
                    out_file.write('\n')
            else:
                with open(filepath, 'w+') as out_file:
                    joined = '\n'.join(dataset)
                    out_file.write(str(joined.encode('utf-8')))
                    out_file.write('\n')


writer(datasets, dataset_names, output_dir)
# Printing out results
print(('%s-%s' % (red, end)) * 50)
for dataset, dataset_name in zip(datasets, dataset_names):
    if dataset:
        print('%s %s: %s' % (good, dataset_name.capitalize(), len(dataset)))
print(('%s-%s' % (red, end)) * 50)

print('%s Total requests made: %i' % (info, len(processed)))
print('%s Total time taken: %i minutes %i seconds' % (info, minutes, seconds))
print('%s Requests per second: %i' % (info, int(len(processed)/diff)))

datasets = {
    'files': list(files), 'intel': list(intel), 'robots': list(robots),
    'custom': list(custom), 'failed': list(failed), 'internal': list(internal),
    'scripts': list(scripts), 'external': list(external),
    'fuzzable': list(fuzzable), 'endpoints': list(endpoints),
    'keys' : list(keys)
}

if args.dns:
    print('%s Enumerating subdomains' % run)
    from plugins.find_subdomains import find_subdomains
    subdomains = find_subdomains(domain)
    print('%s %i subdomains found' % (info, len(subdomains)))
    writer([subdomains], ['subdomains'], output_dir)
    datasets['subdomains'] = subdomains
    from plugins.dnsdumpster import dnsdumpster
    print('%s Generating DNS map' % run)
    dnsdumpster(domain, output_dir)

if args.export:
    from plugins.exporter import exporter
    # exporter(directory, format, datasets)
    exporter(output_dir, args.export, datasets)

print('%s Results saved in %s%s%s directory' % (good, green, output_dir, end))

if args.std:
    for string in datasets[args.std]:
        sys.stdout.write(string + '\n')
