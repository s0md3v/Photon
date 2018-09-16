#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

# Let's import what we need
import os
import sys
import tld
import time
import random
import warnings
import argparse
import threading
from math import log
from re import search, findall
from requests import get, post

try:
    import concurrent.futures
    from urllib.parse import urlparse # for python3
    python2, python3 = False, True
except ImportError:
    from urlparse import urlparse # for python2
    python2, python3 = True, False

from core.config import intels, badTypes

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
    end = '\033[0m'             # finish color
    red = '\033[91m'            # red color
    bold = '\033[1m'            # make text bold
    white = '\033[1;97m'        # gray color
    green = '\033[1;32m'        # green color
    yellow = '\033[1;33m'       # yellow color
    run = '\033[1;97m[*]'+end   # processing ...
    bad = '\033[1;31m[-]'+end   # error or warning
    good = '\033[1;32m[+]'+end  # good news
    info = '\033[1;33m[!]'+end  # some info
    que = '\033[1;34m[?]'+end   # user input

# Just a fancy ass banner
print('''%s      ____  __          __
     / %s__%s \/ /_  ____  / /_____  ____
    / %s/_/%s / __ \/ %s__%s \/ __/ %s__%s \/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\____/\__/\____/_/ /_/ %sv1.1.1%s\n''' %
  (red, white, red, white, red, white, red, white, red, white, red, white, red, white, end))

warnings.filterwarnings('ignore') # Disable SSL related warnings

# Processing command line arguments
parser = argparse.ArgumentParser()
# Options
parser.add_argument('-u', '--url', help='main url (eg. http://www.example.com)', dest='root')
parser.add_argument('-c', '--cookie', help='cookie to be used', dest='cook')
parser.add_argument('-r', '--regex', help='regex pattern', dest='regex')
parser.add_argument('-e', '--export', help='export format type', dest='export')
parser.add_argument('-o', '--output', help='output directory', dest='output')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level', type=int)
parser.add_argument('-t', '--threads', help='number of threads', dest='threads', type=int)
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=float)
parser.add_argument('-s', '--seeds', help='additional seed urls', dest='seeds', nargs="+", default=[])

parser.add_argument('--stdout', help='send variables to stdout', dest='std')
parser.add_argument('--user-agent', help='custom user agent(s)', dest='user_agent')
parser.add_argument('--exclude', help='exclude urls matching this regex', dest='exclude')
parser.add_argument('--timeout', help='http request timeout', dest='timeout', type=float)

# Switches
parser.add_argument('-v', '--verbose', help='verbose output', dest='verbose', action='store_true')
parser.add_argument('--dns', help='enumerate subdomains & dns data', dest='dns', action='store_true')
parser.add_argument('--ninja', help='ninja mode', dest='ninja', action='store_true')
parser.add_argument('--keys', help='find secret keys', dest='api', action='store_true')
parser.add_argument('--update', help='update photon', dest='update', action='store_true')
parser.add_argument('--only-urls', help='only extract urls', dest='only_urls', action='store_true')
parser.add_argument('--wayback', help='fetch urls from archive.org as seeds', dest='archive', action='store_true')
args = parser.parse_args()

####
# This function git clones the latest version and merges it with the current directory
####

def update():
    print('%s Checking for updates' % run)
    changes = '''added the -v option; fixed 2 logic errors in detecting bad js scripts''' # Changes must be seperated by ;
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

####
# This function is for giving out a more verbose output
####

def verb(crawled_type, stuff): 
	if args.verbose: # if '-v' is supplied
		out = r'%s' % stuff # converting it to raw string
		print('%s Found %s: %s%s%s' % (good, crawled_type, bold, stuff, end)) # print it out

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
api = bool(args.api)  # extract high entropy strings i.e. API keys and stuff
ninja = bool(args.ninja)  # Ninja mode toggle
crawl_level = args.level or 2  # Crawling level
thread_count = args.threads or 2  # Number of threads
only_urls = bool(args.only_urls)  # only urls mode is off by default

# Variables we are gonna use later to store stuff
keys = set() # high entropy strings, prolly secret keys
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
internal = set([s for s in args.seeds]) # urls that belong to the target i.e. in-scope

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

schema = main_url.split('//')[0] # https: or http:?

internal.add(main_url) # adding the root url to internal for crawling

host = urlparse(main_url).netloc # Extracts host out of the url

output_dir = args.output or host

####
# This function extracts top level domain from a url
####

def topLevel(url):
    try:
        toplevel = tld.get_fld(host, fix_protocol=True)
    except tld.exceptions.TldDomainNotFound:
        toplevel = urlparse(main_url).netloc
    return toplevel

domain = topLevel(main_url)

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
        # set headers for request
        headers = {
        'Host' : host, # ummm this is the hostname?
        'User-Agent' : random.choice(user_agents), # selecting a random user-agent
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Accept-Encoding' : 'gzip',
        'DNT' : '1',
        'Connection' : 'close'}
        # make request and return response
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

    # pixlr.com API
    def pixlr(url):
        if url == main_url:
            url = main_url + '/' # because pixlr throws error if http://example.com is used
        # make request and return response
        return get('https://pixlr.com/proxy/?url=' + url, headers={'Accept-Encoding' : 'gzip'}, verify=False).text

    # codebeautify.org API
    def code_beautify(url):
        # set headers and get request done
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
# This function extracts links from .xml files
####

def xmlParser(response):
    return findall(r'<loc>(.*?)</loc>', response) # regex for extracting urls

####
# This function extracts links from robots.txt and sitemap.xml
####

def zap(url):
    if args.archive:
        from plugins.wayback import timeMachine
        print ('%s Fetching URLs from archive.org' % run)
        if False:
            archived_urls = timeMachine(domain, 'domain')
        else:
            archived_urls = timeMachine(host, 'host')
        print ('%s Retrieved %i URLs from archive.org' % (good, len(archived_urls) - 1))
        for url in archived_urls:
        	verb('Link', url)
        	internal.add(url)
    response = get(url + '/robots.txt', verify=False).text # makes request to robots.txt
    if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
        matches = findall(r'Allow: (.*)|Disallow: (.*)', response) # If you know it, you know it
        if matches:
            for match in matches: # iterating over the matches, match is a tuple here
                match = ''.join(match) # one item in match will always be empty so will combine both items
                if '*' not in match: # if the url doesn't use a wildcard
                    url = main_url + match
                    verb('Internal Link', url)
                    internal.add(url) # add the url to internal list for crawling
                    robots.add(url) # add the url to robots list
            print('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
    response = get(url + '/sitemap.xml', verify=False).text # makes request to sitemap.xml
    if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
        matches = xmlParser(response)
        if matches: # if there are any matches
            print('%s URLs retrieved from sitemap.xml: %s' % (good, len(matches)))
            for match in matches:
            	verb('Internal Link', match);internal.add(match)
		
         # would consistently give out indentation error why i don't know... drives me crazy... only solution i found :(

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
        if url.split('.')[-1].lower() in badTypes:
        	verb('File', url)
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
        	verb('Link', match)
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
        	verb('Bad Intel',match)
        	bad_intel.add(match) # add it to intel list

####
# This function extracts js files from the response body
####

def js_extractor(response):
    matches = findall(r'src=[\'"](.*?\.js)["\']', response) # extract .js files
    for match in matches: # iterate over the matches
        # using first 2 'if' and 'elif' cases, the no of bad js scripts have most probably gone down to 0
        if match.startswith('/'): # scripts which start with '/' aren't bad js (got to know this after running with the -v option)
            js_script = main_url + match # add to main url
            verb('JS Script', js_script)
            scripts.add(js_script) # add them to scripts list
        elif match.startswith('http'): # if 'http' is there, it is a valid external js script but not a bad js (got to know this after -v)
            verb('External JS Script', match)
            scripts.add(match) # add them to scripts list
        else: # else they might be bad scripts
        	verb('Bad JS Script', match)
        	bad_scripts.add(match) # add to bad intel scripts

####
# This function calculates the entropy of a string to find whether its a key or not
####

def entropy(payload):
    entropy = 0
    for number in range(256):
        result = float(payload.encode('utf-8').count(chr(number)))/len(payload.encode('utf-8'))
        if result != 0:
            entropy = entropy - result * log(result, 2)
    return entropy

####
# This function extracts stuff from the response body
####

def extractor(url):
    response = requester(url) # make request to the url
    matches = findall(r'<[aA].*href=["\']{0,1}(.*?)["\']', response)
    for link in matches: # iterate over the matches
        link = link.split('#')[0] # remove everything after a "#" to deal with in-page anchors
        if is_link(link): # checks if the urls should be crawled
            if link[:4] == 'http': # if url starts with 'http'
                if link.startswith(main_url):
                	verb('Internal Link', link)
                	internal.add(link) # add to main interanl list
                else:
                	verb('External Link', link)
                	external.add(link)
            elif link[:2] == '//': # if link startswith '//'
                if link.split('/')[2].startswith(host):
                	verb('Internal Link', schema + link)
                	internal.add(schema + link)
                else:
                	verb('External Link', link)
                	external.add(link)
            elif link[:1] == '/': # if url starts with '/' (eg. /images/img.png)
            	verb('Internal Link', main_url + link)
            	internal.add(main_url + link)
            else:
            	verb('Internal Link', main_url + '/' + link)
            	internal.add(main_url + '/' + link)

    if not only_urls:
        intel_extractor(response)
        js_extractor(response)
    if args.regex and not supress_regex: # check whether regex is not banned
        regxy(args.regex, response)
    if api:
        matches = findall(r'[\w-]{16,45}', response) # regex for finding keys
        for match in matches:
            if entropy(match) >= 4: # if entropy score > 4 its a possible token or key
            	verb('Key', url + ': ' + match)
            	keys.add(url + ': ' + match)

####
# This function extracts endpoints from JavaScript Code
####

def jscanner(url):
    response = requester(url) # make request to the url
    matches = findall(r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]', response) # extract urls/endpoints
    for match in matches: # iterate over the matches, match is a tuple
        match = match[0] + match[1] # combining the items because one of them is always empty
        if not search(r'[}{><"\']', match) and not match == '/': # making sure it's not some js code
        	verb('JS Endpoint', match)
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
# This function processes the urls and uses a threadpool to execute a function
####

def flash(function, links): # This shit is NOT complicated, please enjoy
    links = list(links) # convert links (set) to list
    if sys.version_info < (3, 2):
        for begin in range(0, len(links), thread_count): # range with step
            end = begin + thread_count
            splitted = links[begin:end]
            threader(function, splitted) # start the multithreading
            progress = end
            if progress > len(links): # fix if overflow
                progress = len(links)
            print('\r%s Progress: %i/%i' % (info, progress, len(links)), end='\r')
    else:
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)
        futures = (threadpool.submit(function, link) for link in links)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(links) or (i + 1) % thread_count == 0:
                print('\n%s Progress: %i/%i' % (info, i + 1, len(links)), end='\r') # had to put '\n' as it was causing some lines to bump in
    print('')

then = time.time() # records the time at which crawling started

# Step 1. Extract urls from robots.txt & sitemap.xml
zap(main_url)

# this is so the level 1 emails are parsed as well
internal = set(remove_regex(internal, args.exclude))

# Step 2. Crawl recursively to the limit specified in "crawl_level"
for level in range(crawl_level):
    links = remove_regex(internal - processed, args.exclude) # links to crawl = (all links - already crawled links) - links not to crawl
    if not links: # if links to crawl are 0 i.e. all links have been crawled
        break
    elif len(internal) <= len(processed): # if crawled links are somehow more than all links. Possible? ;/
        if len(internal) > 2 + len(args.seeds): # if you know it, you know it
            break
    print('%s Level %i: %i URLs' % (run, level + 1, len(links)))
    try:
        flash(extractor, links)
    except KeyboardInterrupt: # if user breaks runtime
        print('')
        break

if not only_urls:
    for match in bad_scripts: # check if script not in bad js scripts
        if match.startswith(main_url):
        	verb('JS File', match)
        	scripts.add(match) # add js scripts
        elif match.startswith('/') and not match.startswith('//'):
        	verb('JS File', main_url + match)
        	scripts.add(main_url + match)
        elif not match.startswith('http') and not match.startswith('//'):
        	verb('JS File', main_url + '/' + match)
        	scripts.add(main_url + '/' + match)
    # Step 3. Scan the JavaScript files for enpoints
    print('%s Crawling %i JavaScript files' % (run, len(scripts)))
    flash(jscanner, scripts)

    for url in internal:
        if '=' in url:
        	verb('Fuzzable Param', url)
        	fuzzable.add(url) # append to fuzzable parameters list

    for match in bad_intel:
        for x in match: # because "match" is a tuple
            if x != '': # if the value isn't empty
            	verb('Intel', x)
            	intel.add(x) # append to fuzzable parameters list
        for url in external:
            try:
                if tld.get_fld(url, fix_protocol=True) in intels:
                	verb('Intel', url)
                	intel.add(url) # add to intel list
            except:
                pass

now = time.time() # records the time at which crawling stopped
diff = (now - then) # finds total time taken

def timer(diff):
    minutes, seconds = divmod(diff, 60) # Changes seconds into minutes and seconds
    try:
        time_per_request = diff / float(len(processed)) # Finds average time taken by requests
    except ZeroDivisionError: # if float(len(processed)) == 0
        time_per_request = 0
    return minutes, seconds, time_per_request
minutes, seconds, time_per_request = timer(diff)

# Step 4. Save the results
if not os.path.exists(output_dir): # if the directory doesn't exist
    os.mkdir(output_dir) # create a new directory

datasets = [files, intel, robots, custom, failed, internal, scripts, external, fuzzable, endpoints, keys] # list of all extracted types
dataset_names = ['files', 'intel', 'robots', 'custom', 'failed', 'internal', 'scripts', 'external', 'fuzzable', 'endpoints', 'keys'] # as str

####
# This function writes the crawled links and files to different files
####

def writer(datasets, dataset_names, output_dir):
    for dataset, dataset_name in zip(datasets, dataset_names):
        if dataset:
            filepath = output_dir + '/' + dataset_name + '.txt'
            if python3: # if machine running python 3
                with open(filepath, 'w+', encoding='utf8') as f: # make sure no encoding #errors
                    f.write(str('\n'.join(dataset)))
                    f.write('\n')
            else: # else if python2
                with open(filepath, 'w+') as f:
                    joined = '\n'.join(dataset)
                    f.write(str(joined.encode('utf-8'))) # make sure no encoding errors
                    f.write('\n')

writer(datasets, dataset_names, output_dir)
# Printing out results
print (('%s-%s' % (red, end)) * 50)
for dataset, dataset_name in zip(datasets, dataset_names):
    if dataset:
        print ('%s %s: %s' % (good, dataset_name.capitalize(), len(dataset)))
print (('%s-%s' % (red, end)) * 50)

print('%s Total requests made: %i' % (info, len(processed)))
print('%s Total time taken: %i minutes %i seconds' % (info, minutes, seconds))
print('%s Requests per second: %i' % (info, int(len(processed)/diff)))

datasets = {
'files': list(files), 'intel': list(intel), 'robots': list(robots), 'custom': list(custom), 'failed': list(failed), 'internal': list(internal),
'scripts': list(scripts), 'external': list(external), 'fuzzable': list(fuzzable), 'endpoints': list(endpoints), 'keys' : list(keys)
}

if args.dns:
    print ('%s Enumerating subdomains' % run)
    from plugins.findSubdomains import findSubdomains
    subdomains = findSubdomains(domain)
    print ('%s %i subdomains found' % (info, len(subdomains)))
    writer([subdomains], ['subdomains'], output_dir)
    datasets['subdomains'] = subdomains
    from plugins.dnsdumpster import dnsdumpster
    print ('%s Generating DNS map' % run)
    dnsdumpster(domain, output_dir)

if args.export:
    from plugins.exporter import exporter
    # exporter(directory, format, datasets)
    exporter(output_dir, args.export, datasets)

print('%s Results saved in %s%s%s/ directory' % (good, green, output_dir, end))

if args.std:
    for string in datasets[args.std]:
        sys.stdout.write(string + '\n')
