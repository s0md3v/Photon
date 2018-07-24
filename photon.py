#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Let's import what we need
import os
import sys
import time
import shutil
import random
import urllib3
import argparse
import threading
from re import search, findall
from requests import get, post, codes
try:
    from urllib.parse import urlparse # for python3
except ImportError:
    from urlparse import urlparse # for python2

colors = True # Output should be colored
machine = sys.platform # Detecting the os of current system
if machine.startswith('os') or machine.startswith('win') or machine.startswith('darwin') or machine.startswith('ios'):
    colors = False # Colors shouldn't be displayed in mac & windows
if not colors:
    end = red = white = green = yellow = run = bad = good = info = que =  '' 
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
    que =  '\033[1;34m[?]\033[1;m'

# Just a fancy ass banner
print ('''%s      ____  __          __            
     / %s__%s \/ /_  ____  / /_____  ____ 
    / %s/_/%s / __ \/ %s__%s \/ __/ %s__%s \/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\____/\__/\____/_/ /_/ %s\n''' %
  (red, white, red, white, red, white, red, white, red, white, red, white, red, end))

urllib3.disable_warnings() # Disable SSL related warnings

# Processing command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='root url', dest='root')
parser.add_argument('-c', '--cookie', help='cookie', dest='cook')
parser.add_argument('-r', '--regex', help='regex pattern', dest='regex')
parser.add_argument('-s', '--seeds', help='additional seed urls', dest='seeds')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level', type=int)
parser.add_argument('-t', '--threads', help='number of threads', dest='threads', type=int)
parser.add_argument('-n', '--ninja', help='ninja mode', dest='ninja', action='store_true')
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=int)
args = parser.parse_args()

if args.root: # if the user has supplied a url
    main_inp = args.root
    if main_inp.endswith('/'): # if the url ends with '/'
        main_inp = main_inp[:-1] # we will remove it as it can cause problems later in the code
else: # if the user hasn't supplied a url
    print ('\n' + parser.format_help().lower())
    quit()

delay = 0 # Delay between requests
cook = None # Cookie
ninja = False # Ninja mode toggle
crawl_level = 2 # Crawling level
thread_count = 2 # Number of threads

if args.cook:
    cook = args.cook
if args.ninja:
    ninja = True
if args.delay:
    delay = args.delay
if args.level:
    crawl_level = args.level
if args.threads:
    thread_count = args.threads

# Variables we are gonna use later to store stuff
files = set() # pdf, css, png etc.
intel = set() # emails, website accounts, aws buckets etc.
robots = set() # entries of robots.txt
custom = set() # string extracted by custom regex pattern
failed = set() # urls that photon failed to crawl
storage = set() # urls that belong to the target i.e. in-scope
scripts = set() # javascript files
external = set() # urls that don't belong to the target i.e. out-of-scope
fuzzable = set() # urls that have get params in them e.g. example.com/page.php?id=2
endpoints = set() # urls found from javascript files
processed = set() # urls that have been crawled

seeds = '' # custom urls to crawl
if args.seeds: # if the user has supplied custom seeds
    seeds = args.seeds
    for seed in seeds.split(','): # we will convert them into a list
        storage.add(seed) # and them to storage for crawling

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

name = urlparse(main_url).netloc # Extracts domain out of the url

####
# This function makes requests to webpage and returns response body
####

# list of user agents
user_agents = ['Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991']

def requester(url):
    processed.add(url) # mark the url as crawled
    time.sleep(delay) # pause/sleep the program for specified time
    try:
        def normal(url):
            headers = {
            'Host' : name, # ummm this is the hostname?
            'User-Agent' : random.choice(user_agents), # selecting a random user-agent
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip',
            'DNT' : '1',
            'Connection' : 'close'}
            # make request and return response
            return get(url, cookies=cook, headers=headers, verify=False)

        # pixlr.com API
        def pixlr(url):
            if url == main_url:
                url = main_url + '/' # because pixlr throws error if http://example.com is used
            # make request and return response
            return get('https://pixlr.com/proxy/?url=' + url, headers={'Accept-Encoding' : 'gzip'}, verify=False)

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
            return post('https://codebeautify.com/URLService', headers=headers, data='path=' + url, verify=False)

        # www.photopea.com API
        def photopea(url):
            # make request and return response
            return get('https://www.photopea.com/mirror.php?url=' + url, verify=False)

        if ninja: # if the ninja mode is enabled
            # select a random request function i.e. random API
            response = random.choice([photopea, normal, pixlr, code_beautify])(url)
            
            #check if link is not broken
            if response.status_code == codes.ok:
                return response.text  # return response body
            else:
                failed.add(url) # add it to the failed list

        else:
            response = normal(url)

            #check if link is not broken
            if response.status_code == codes.ok:
                return response.text  # return response body
            else:
                failed.add(url) # add it to the failed list

    except: # if photon fails to connect to the url
        failed.add(url) # add it to the failed list

####
# This function extracts links from robots.txt and sitemap.xml
####

def zap(url):
    try:
        response = requester(url + '/robots.txt') # makes request to robots.txt
        if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
            matches = findall(r'Allow: (.*)|Disallow: (.*)', response) # If you know it, you know it
            for match in matches: # iterating over the matches, match is a tuple here
                match = match[0] + match[1] # one item in match will always be empty so will combine both items
                if '/*/' not in match: # if the url doesn't use a wildcard
                    url = main_url + match
                    storage.add(url) # add the url to storage list for crawling
                    robots.add(url) # add the url to robots list
                    if '=' in url: # self-explanatory
                        fuzzable.add(url) # add url to the fuzzable urls list
            if len(matches) > 0: # if there are more than 0 matches
                print ('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
        
        response = requester(url + '/sitemap.xml') # makes request to sitemap.xml
        
        if '<body' not in response: # making sure robots.txt isn't some fancy 404 page
            matches = findall(r'<loc>[^<]*</loc>', response) # regex for extracting urls
            if matches: # if there are any matches
                print ('%s URLs retrieved from sitemap.xml: %s' % (good, len(matches)))
                for match in matches:
                    storage.add(match.split('<loc>')[1][:-6]) #cleaning up the url & adding it to the storage list for crawling
    except:
        pass
####
# This functions checks whether a url should be crawled or not
####

def is_link(url):
    # file extension that don't need to be crawled and are files
    bad = ['xml', 'png', 'bmp', 'jpg', 'jpeg', 'pdf', 'css', 'ico', 'js', 'svg', 'json']
    conclusion = False # whether the the url should be crawled or not
    
    if url not in processed: # if the url hasn't been crawled already
        if '.' in url[-5:]: # url[-5:] = last 5 chars of url
            extension = url[-5:].split('.')[-1] # finding the extension of webpage
            if extension not in bad: # if the extension isn't "bad"
                conclusion = True # url can be crawled
            else:
                files.add(main_url + url) # its a file
        else: # it has no extension
            return True # url can be crawled
    return conclusion # return the conclusion :D

####
# This function extracts stuff from the response body
####

def extractor(url):
    response = requester(url) # make request to the url
    try:
        matches = findall(r'href=[\'"](.*?)["\']', response) # find all the linkx
        for link in matches: # iterate over the matches
            link = link.split('#')[0] # remove everything after a "#" to deal with in-page anchors
            if is_link(link): # checks if the urls should be crawled
                if link.startswith(main_url): # self-explanatory
                    storage.add(link)
                    if '=' in link:
                        fuzzable.add(link)
                if link.startswith('http') or link.startswith('//'):
                    if not link.startswith(main_url):
                        external.add(link)
                elif link.startswith('javascript') or link.startswith('{{'):
                    pass # we aren't fucking with javascript
                elif link.startswith('/') and not link.startswith('//'):
                    storage.add(main_url + link)
                    if '=' in link:
                        fuzzable.add(link)
                elif not link.startswith('http') and not link.startswith('//'):
                    storage.add(main_url + '/' + link)
                    if '=' in link:
                        fuzzable.add(link)
        
        matches = findall(r'src=[\'"](.*?\.js)["\']', response) # extract .js files
        for match in matches: # iterate over the matches
            if match.startswith(main_url):
                scripts.add(match)
            elif match.startswith('/') and not match.startswith('//'):
                scripts.add(main_url + match)
            elif not match.startswith('http') and not match.startswith('//'):
                scripts.add(main_url + '/' + match)
        # extract intel ;)
        matches = findall(r'''([\w\.-]+s[\w\.-]+\.amazonaws\.com)|(github\.com/[\w\.-/]+)|(facebook\.com/.*?)[\'" ]|
(youtube\.com/.*?)[\'" ]|(linkedin\.com/.*?)[\'" ]|(twitter\.com/.*?)[\'" ]|([\w\.-]+@[\w\.-]+\.[\.\w]+)''', response)
        for match in matches: # iterate over the matches
            for x in match: # iterate over the match because it's a tuple
                if x != '': # if the value isn't empty
                    intel.add(x) # add it to intel list

        def regxy(pattern):
            matches = findall(r'%s' % pattern, response)
            for match in matches:
                custom.add(match)
        if args.regex:
            regxy(args.regex)

    except: # if something bad happens
        failed.add(url)

####
# This function extracts endpoints from JavaScript Code
####

def jscanner(url):
    try:
        response = requester(url) # make request to the url
        matches = findall(r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]', response) # extract urls/endpoints
        for match in matches: # iterate over the matches, match is a tuple
            match = match[0] + match[1] # combining the items because one of them is always empty
            if not search(r'[}{><"\']', match) and not match == '/': # making sure it's not some js code
                endpoints.add(match) # add it to the endpoints list
    except:
        failed.add(url)

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

def flash(function, links): # This shit is complicated, move on
    links = list(links) # convert links (set) to list
    begin = 0 # begining of slice
    end = thread_count # ending of slice
    # Okay I give up, if you know it, you know it
    for i in range((int(len(links)/thread_count)) + 1):
        splitted = links[begin:end]
        threader(function, splitted)
        begin += thread_count
        if (len(links) - end) >= thread_count:
            end += thread_count
        else:
            end += len(links) - begin
        progress = begin
        if progress > len(links):
            progress = len(links)
        sys.stdout.write('\r%s Progress: %i/%i' % (info, progress, len(links)))
        sys.stdout.flush()
    print ('')

then = time.time() # records the time at which crawling started

# Step 1. Extract urls from robots.txt & sitemap.xml
zap(main_url)

# Step 2. Crawl recursively to the limit specified in "crawl_level"
for level in range(crawl_level):
    links = storage - processed # links to crawl = all links - already crawled links
    if len(links) == 0: # if links to crawl are 0 i.e. all links have been crawled
        break
    if len(storage) <= len(processed): # if crawled links are somehow more than all links. Possible? ;/
        if len(storage) > 2 + len(seeds): # if you know it, you know it
            break
    print ('%s Level %i: %i URLs' % (run, level + 1, len(links)))
    try:
        flash(extractor, links)
    except KeyboardInterrupt:
        print ('')
        break

# Step 3. Scan the JavaScript files for enpoints
print ('%s Crawling %i JavaScript files' % (run, len(scripts)))
flash(jscanner, scripts)

now = time.time() # records the time at which crawling stopped
diff = (now  - then) # finds total time taken

def timer(diff):
    minutes, seconds = divmod(diff, 60) # Changes seconds into minutes and seconds
    time_per_request = diff / float(len(processed)) # Finds average time taken by requests
    return minutes, seconds, time_per_request
time_taken = timer(diff)
minutes = time_taken[0]
seconds = time_taken[1]
time_per_request = time_taken[2]
# Step 4. Save the results
if os.path.exists(name): # if the directory already exists
    shutil.rmtree(name, ignore_errors=True) # delete it, recursively
os.mkdir(name) # create a new directory

with open('%s/links.txt' % name, 'w+') as f:
    for x in storage:
        f.write(x + '\n')

with open('%s/files.txt' % name, 'w+') as f:
    for x in files:
        f.write(x + '\n')

with open('%s/intel.txt' % name, 'w+') as f:
    for x in intel:
        f.write(x + '\n')

with open('%s/robots.txt' % name, 'w+') as f:
    for x in storage:
        f.write(x + '\n')

with open('%s/failed.txt' % name, 'w+') as f:
    for x in failed:
        f.write(x + '\n')

with open('%s/custom.txt' % name, 'w+') as f:
    for x in custom:
        f.write(x + '\n')

with open('%s/scripts.txt' % name, 'w+') as f:
    for x in scripts:
        f.write(x + '\n')

with open('%s/fuzzable.txt' % name, 'w+') as f:
    for x in fuzzable:
        f.write(x + '\n')

with open('%s/external.txt' % name, 'w+') as f:
    for x in external:
        f.write(x + '\n')

with open('%s/endpoints.txt' % name, 'w+') as f:
    for x in endpoints:
        f.write(x + '\n')

# Printing out results
print ('''%s
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

print ('%s Total time taken: %i:%i' % (info, minutes, seconds))
print ('%s Average request time: %s' % (info, str(time_per_request)[:4]))

if not colors: # if colors are disabled
    print ('%s Results saved in %s directory' % (good, name))
else:
    print ('%s Results saved in \033[;1m%s\033[0m directory' % (good, name))
