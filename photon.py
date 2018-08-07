#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Let's import what we need
import os
import sys
import time
import random
import warnings
import argparse
import threading
from re import search, findall
from requests import get, post

try:
    from urllib.parse import urlparse # for python3
    python2, python3 = False, True
except ImportError:
    from urlparse import urlparse # for python2
    python2, python3 = True, False

try:
    input = raw_input
except NameError:
    pass

colors = True # Output should be colored
machine = sys.platform # Detecting the os of current system
if machine.lower().startswith(('os', 'win', 'darwin', 'ios')):
    colors = False # Colors shouldn't be displayed in mac & windows
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
  /_/   /_/ /_/\____/\__/\____/_/ /_/ %sv1.0.7%s\n''' %
  (red, white, red, white, red, white, red, white, red, white, red, white, red, white, end))

warnings.filterwarnings('ignore') # Disable SSL related warnings

# Processing command line arguments
parser = argparse.ArgumentParser()
# Options
parser.add_argument('-u', '--url', help='root url', dest='root')
parser.add_argument('-c', '--cookie', help='cookie', dest='cook')
parser.add_argument('-r', '--regex', help='regex pattern', dest='regex')
parser.add_argument('-e', '--export', help='export format', dest='export')
parser.add_argument('-o', '--output', help='output directory', dest='output')
parser.add_argument('-s', '--seeds', help='additional seed urls', dest='seeds', nargs="+", default=[])
parser.add_argument('--user-agent', help='custom user agent(s)', dest='user_agent')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level', type=int)
parser.add_argument('--timeout', help='http request timeout', dest='timeout', type=float)
parser.add_argument('-t', '--threads', help='number of threads', dest='threads', type=int)
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=float)
parser.add_argument('--exclude', help='exclude urls matching this regex', dest='exclude', type=str)
# Switches
parser.add_argument('--dns', help='dump dns data', dest='dns', action='store_true')
parser.add_argument('--ninja', help='ninja mode', dest='ninja', action='store_true')
parser.add_argument('--update', help='update photon', dest='update', action='store_true')
parser.add_argument('--only-urls', help='only extract urls', dest='only_urls', action='store_true')
args = parser.parse_args()

####
# This function git clones the latest version and merges it with the current directory
####

def update():
    print('%s Checking for updates' % run)
    changes = '''--exclude option to exclude urls with regex;minor refactor''' # Changes must be seperated by ;
    latest_commit = get('https://raw.githubusercontent.com/s0md3v/Photon/master/photon.py').text

    if changes not in latest_commit: # just a hack to see if a new version is available
        changelog = search(r"changes = '''(.*?)'''", latest_commit)
        changelog = changelog.group(1).split(';') # splitting the changes to form a list
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
            os.system('git clone --quiet https://github.com/s0md3v/Photon %s' % (folder))
            os.system('cp -r %s/%s/* %s && rm -r %s/%s/ 2>/dev/null' % (path, folder, path, path, folder))
            print('%s Update successful!' % good)
    else:
        print('%s Photon is up to date!' % good)

if args.update: # if the user has supplied --update argument
    update()
    quit() # quitting because files have been changed

if args.root: # if the user has supplied a url
    main_inp = args.root
    if main_inp.endswith('/'): # if the url ends with '/'
        main_inp = main_inp[:-1] # we will remove it as it can cause problems later in the code
else: # if the user hasn't supplied a url
    print('\n' + parser.format_help().lower())
    quit()

delay = args.delay or 0  # Delay between requests
timeout = args.timeout or 6  # HTTP request timeout
cook = args.cook or None  # Cookie
ninja = bool(args.ninja)  # Ninja mode toggle
crawl_level = args.level or 2  # Crawling level
thread_count = args.threads or 2  # Number of threads
only_urls = bool(args.only_urls)  # only urls mode is off by default

# Variables we are gonna use later to store stuff
files = set() # pdf, css, png etc.
intel = set() # emails, website accounts, aws buckets etc.
robots = set() # entries of robots.txt
custom = set() # string extracted by custom regex pattern
failed = set() # urls that photon failed to crawl
scripts = set() # javascript files
external = set() # urls that don't belong to the target i.e. out-of-scope
fuzzable = set() # urls that have get params in them e.g. example.com/page.php?id=2
endpoints = set() # urls found from javascript files
processed = set() # urls that have been crawled
storage = set([s for s in args.seeds]) # urls that belong to the target i.e. in-scope

everything = []
bad_intel = set() # unclean intel urls
bad_scripts = set() # unclean javascript file urls

# If the user hasn't supplied the root url with http(s), we will handle it
if main_inp.startswith('http'):
    main_url = main_inp
else:
    try:
        get('https://' + main_inp)
        main_url = 'https://' + main_inp
    except:
        main_url = 'http://' + main_inp

storage.add(main_url) # adding the root url to storage for crawling

domain_name = urlparse(main_url).netloc # Extracts domain out of the url

output_dir = args.output or domain_name

####
# This function makes requests to webpage and returns response body
####

if args.user_agent:
    user_agents = args.user_agent.split(',')
else:
    with open(sys.path[0] + '/core/user-agents.txt', 'r') as uas:
        user_agents = [agent.strip('\n') for agent in uas]

def requester(url):
    processed.add(url) # mark the url as crawled
    time.sleep(delay) # pause/sleep the program for specified time
    def normal(url):
        headers = {
        'Host' : domain_name, # ummm this is the hostname?
        'User-Agent' : random.choice(user_agents), # selecting a random user-agent
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Accept-Encoding' : 'gzip',
        'DNT' : '1',
        'Connection' : 'close'}
        # make request and return response
        try:
            response = get(url, cookies=cook, headers=headers, verify=False, timeout=timeout, stream=True)
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
        except:
            return 'dummy'

    # pixlr.com API
    def pixlr(url):
        if url == main_url:
            url = main_url + '/' # because pixlr throws error if http://example.com is used
        # make request and return response
        return get('https://pixlr.com/proxy/?url=' + url, headers={'Accept-Encoding' : 'gzip'}, verify=False).text

    # codebeautify.org API
    def code_beautify(url):
        headers = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept' : 'text/plain, */*; q=0.01',
        'Accept-Encoding' : 'gzip',
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin' : 'https://codebeautify.org',
        'Connection' : 'close'
        }
        # make request and return response
        return post('https://codebeautify.com/URLService', headers=headers, data='path=' + url, verify=False).text

    # www.photopea.com API
    def photopea(url):
        # make request and return response
        return get('https://www.photopea.com/mirror.php?url=' + url, verify=False).text

    if ninja: # if the ninja mode is enabled
        # select a random request function i.e. random API
        response = random.choice([photopea, normal, pixlr, code_beautify])(url)
        return response or 'dummy'
    else:
        return normal(url)

####
# This function extracts links from robots.txt and sitemap.xml
####

def zap(url):
    response = get(url + '/robots.txt').text # makes request to robots.txt
    if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
        matches = findall(r'Allow: (.*)|Disallow: (.*)', response) # If you know it, you know it
        if matches:
            for match in matches: # iterating over the matches, match is a tuple here
                match = ''.join(match) # one item in match will always be empty so will combine both items
                if '*' not in match: # if the url doesn't use a wildcard
                    url = main_url + match
                    storage.add(url) # add the url to storage list for crawling
                    robots.add(url) # add the url to robots list
            print('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
    response = get(url + '/sitemap.xml').text # makes request to sitemap.xml
    if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
        matches = findall(r'<loc>[^<]*</loc>', response) # regex for extracting urls
        if matches: # if there are any matches
            print('%s URLs retrieved from sitemap.xml: %s' % (good, len(matches)))
            for match in matches:
                storage.add(match.split('<loc>')[1][:-6]) #cleaning up the url & adding it to the storage list for crawling

####
# This functions checks whether a url matches a regular expression
####

def remove_regex(urls, regex):
    """
    Parses a list for non-matches to a regex

    Args:
        urls: iterable of urls
        custom_regex: string regex to be parsed for

    Returns:
        list of strings not matching regex
    """

    if not regex:
        return urls

    # to avoid iterating over the characters of a string
    if not isinstance(urls, (list, set, tuple)):
        urls = [urls]

    try:
        non_matching_urls = [url for url in urls if not search(regex, url)]
    except TypeError:
        return []

    return non_matching_urls


####
# This functions checks whether a url should be crawled or not
####

def is_link(url):
    # file extension that don't need to be crawled and are files
    conclusion = False # whether the the url should be crawled or not

    if url not in processed: # if the url hasn't been crawled already
        if '.png' in url or '.jpg' in url or '.jpeg' in url or '.js' in url or '.css' in url or '.pdf' in url or '.ico' in url or '.bmp' in url or '.svg' in url or '.json' in url or '.xml' in url:
            files.add(url)
        else:
            return True # url can be crawled
    return conclusion # return the conclusion :D

####
# This function extracts string based on regex pattern supplied by user
####

supress_regex = False
def regxy(pattern, response):
    try:
        matches = findall(r'%s' % pattern, response)
        for match in matches:
            custom.add(match)
    except:
        supress_regex = True

####
# This function extracts intel from the response body
####

def intel_extractor(response):
    matches = findall(r'''([\w\.-]+s[\w\.-]+\.amazonaws\.com)|([\w\.-]+@[\w\.-]+\.[\.\w]+)''', response)
    if matches:
        for match in matches: # iterate over the matches
            bad_intel.add(match) # add it to intel list
####
# This function extracts js files from the response body
####

def js_extractor(response):
    matches = findall(r'src=[\'"](.*?\.js)["\']', response) # extract .js files
    for match in matches: # iterate over the matches
        bad_scripts.add(match)

####
# This function extracts stuff from the response body
####

def extractor(url):
    response = requester(url) # make request to the url
    matches = findall(r'<[aA].*href=["\']{0,1}(.*?)["\']', response)
    for link in matches: # iterate over the matches
        link = link.split('#')[0] # remove everything after a "#" to deal with in-page anchors
        if is_link(link): # checks if the urls should be crawled
            if link[:4] == 'http':
                if link.startswith(main_url):
                    storage.add(link)
                else:
                    external.add(link)
            elif link[:2] == '//':
                if link.split('/')[2].startswith(domain_name):
                    storage.add(link)
                else:
                    external.add(link)
            elif link[:1] == '/':
                storage.add(main_url + link)
            else:
                storage.add(main_url + '/' + link)

    if not only_urls:
        intel_extractor(response)
        js_extractor(response)
    if args.regex and not supress_regex:
        regxy(args.regex, response)

####
# This function extracts endpoints from JavaScript Code
####

def jscanner(url):
    response = requester(url) # make request to the url
    matches = findall(r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]', response) # extract urls/endpoints
    for match in matches: # iterate over the matches, match is a tuple
        match = match[0] + match[1] # combining the items because one of them is always empty
        if not search(r'[}{><"\']', match) and not match == '/': # making sure it's not some js code
            endpoints.add(match) # add it to the endpoints list

####
# This function starts multiple threads for a function
####

def threader(function, *urls):
    threads = [] # list of threads
    urls = urls[0] # because urls is a tuple
    for url in urls: # iterating over urls
        task = threading.Thread(target=function, args=(url,))
        threads.append(task)
    # start threads
    for thread in threads:
        thread.start()
    # wait for all threads to complete their work
    for thread in threads:
        thread.join()
    # delete threads
    del threads[:]

####
# This function processes the urls and sends them to "threader" function
####

def flash(function, links): # This shit is NOT complicated, please enjoy
    links = list(links) # convert links (set) to list
    for begin in range(0, len(links), thread_count): # range with step
        end = begin + thread_count
        splitted = links[begin:end]
        threader(function, splitted)
        progress = end
        if progress > len(links): # fix if overflow
            progress = len(links)
        sys.stdout.write('\r%s Progress: %i/%i' % (info, progress, len(links)))
        sys.stdout.flush()
    print('')

then = time.time() # records the time at which crawling started

# Step 1. Extract urls from robots.txt & sitemap.xml
zap(main_url)

# this is so the level 1 emails are parsed as well
storage = set(remove_regex(storage, args.exclude))

# Step 2. Crawl recursively to the limit specified in "crawl_level"
for level in range(crawl_level):
    links = remove_regex(storage - processed, args.exclude) # links to crawl = all links - already crawled links
    if not links: # if links to crawl are 0 i.e. all links have been crawled
        break
    elif len(storage) <= len(processed): # if crawled links are somehow more than all links. Possible? ;/
        if len(storage) > 2 + len(args.seeds): # if you know it, you know it
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
    # Step 3. Scan the JavaScript files for enpoints
    print('%s Crawling %i JavaScript files' % (run, len(scripts)))
    flash(jscanner, scripts)

    for url in storage:
        if '=' in url:
            fuzzable.add(url)

    for match in bad_intel:
        for x in match: # because "match" is a tuple
            if x != '': # if the value isn't empty
                intel.add(x)

    for url in external:
        if 'github.com' in url or 'facebook.com' in url or 'instagram.com' in url or 'youtube.com' in url:
            intel.add(url)

now = time.time() # records the time at which crawling stopped
diff = (now - then) # finds total time taken

def timer(diff):
    minutes, seconds = divmod(diff, 60) # Changes seconds into minutes and seconds
    try:
        time_per_request = diff / float(len(processed)) # Finds average time taken by requests
    except ZeroDivisionError:
        time_per_request = 0
    return minutes, seconds, time_per_request
minutes, seconds, time_per_request = timer(diff)

# Step 4. Save the results
if not os.path.exists(output_dir): # if the directory doesn't exist
    os.mkdir(output_dir) # create a new directory

datasets = [files, intel, robots, custom, failed, remove_regex(storage, args.exclude), scripts, external, fuzzable, endpoints]
dataset_names = ['files', 'intel', 'robots', 'custom', 'failed', 'links', 'scripts', 'external', 'fuzzable', 'endpoints']

def writer(datasets, dataset_names, output_dir):
    for dataset, dataset_name in zip(datasets, dataset_names):
        if dataset:
            filepath = output_dir + '/' + dataset_name + '.txt'
            if python3:
                with open(filepath, 'w+', encoding='utf8') as f:
                    f.write(str('\n'.join(dataset)))
            else:
                with open(filepath, 'w+') as f:
                    joined = '\n'.join(dataset)
                    f.write(str(joined.encode('utf-8')))

writer(datasets, dataset_names, output_dir)
# Printing out results
print('''%s
%s URLs: %i
%s Intel: %i
%s Files: %i
%s Endpoints: %i
%s Fuzzable URLs: %i
%s Custom strings: %i
%s JavaScript Files: %i
%s External References: %i
%s''' % ((('%s-%s' % (red, end)) * 50), good, len(storage), good,
len(intel), good, len(files), good, len(endpoints), good, len(fuzzable), good,
len(custom), good, len(scripts), good, len(external),
(('%s-%s' % (red, end)) * 50)))

print('%s Total time taken: %i minutes %i seconds' % (info, minutes, seconds))
print('%s Average request time: %s seconds' % (info, time_per_request))

if args.dns:
    from plugins.dnsdumpster import dnsdumpster
    dnsdumpster(domain_name, output_dir, colors)

if args.export:
    datasets = {
    'files': list(files), 'intel': list(intel), 'robots': list(robots), 'custom': list(custom), 'failed': list(failed),
    'storage': list(storage), 'scripts': list(scripts), 'external': list(external), 'fuzzable': list(fuzzable), 'endpoints': list(endpoints)
    }
    from plugins.exporter import exporter
    # exporter(directory, format, datasets)
    exporter(output_dir, args.export, datasets)

print('%s Results saved in %s%s%s directory' % (good, green, output_dir, end))
