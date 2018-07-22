#!/usr/bin/env python3

# Colors and shit bro
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

# Let's import what we need
import os
import sys
import time
import random
import urllib3
import argparse
import threading
from requests import get, post
from re import search, findall
from urllib.parse import urlparse

print ('''%s      ____  __          __            
     / %s__%s \/ /_  ____  / /_____  ____ 
    / %s/_/%s / __ \/ %s__%s \/ __/ %s__%s \/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\____/\__/\____/_/ /_/ %s\n''' % (red, white, red, white, red, white, red, white, red, white, red, white, red, end))

urllib3.disable_warnings()

# Processing command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='root url', dest='root')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level', type=int)
parser.add_argument('-t', '--threads', help='number of threads', dest='threads', type=int)
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=int)
parser.add_argument('-c', '--cookie', help='cookie', dest='cook')
parser.add_argument('-s', '--seeds', help='additional seed urls', dest='seeds')
parser.add_argument('-n', '--ninja', help='ninja mode', dest='ninja', action='store_true')
args = parser.parse_args()

if args.root:
    main_inp = args.root
else:
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
files = set()
intel = set()
robots = set()
failed = set()
storage = set()
scripts = set()
external = set()
fuzzable = set()
endpoints = set()
processed = set()

seeds = ''
if args.seeds:
    seeds = args.seeds
    for seed in seeds.split(','):
        storage.add(seed)

# If the user hasn't supplied the root url with http(s), we will handle it
if main_inp.startswith('http'):
    main_url = main_inp
else:
    try:
        get('https://' + main_inp)
        main_url = 'https://' + main_inp
    except:
        main_url = 'http://' + main_inp

storage.add(main_url)

main_domain = urlparse(main_url).netloc # Extracts domain out of the url
name = main_domain.split('.')[-2] # Extracts example out of example.com

####
# This function makes requests to webpage and returns response body
####

user_agents = ['Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991']

def requester(url):
    processed.add(url)
    time.sleep(delay)
    try:
        def normal(url):
            headers = {
            'Host' : main_domain,
            'User-Agent' : random.choice(user_agents),
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip',
            'DNT' : '1',
            'Connection' : 'close'}
            return get(url, cookies=cook, headers=headers, verify=False).text

        def pixlr(url):
            if url == main_url:
                url = main_url + '/'
            return get('https://pixlr.com/proxy/?url=' + url, headers={'Accept-Encoding' : 'gzip'}, verify=False).text

        def code_beautify(url):
            headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept' : 'text/plain, */*; q=0.01',
            'Accept-Encoding' : 'gzip',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin' : 'https://codebeautify.org',
            'Connection' : 'close'
            }
            return post('https://codebeautify.com/URLService', headers=headers, data='path=' + url, verify=False).text

        def photopea(url):
            return get('https://www.photopea.com/mirror.php?url=' + url, verify=False).text

        if ninja:
            return random.choice([photopea, normal, pixlr, code_beautify])(url)
        else:
            return normal(url)
    except:
        failed.add(url)

####
# This function extracts links from robots.txt and sitemap.xml
####

def zap(url):
    response = requester(url + '/robots.txt')
    if '<body' not in response:
        matches = findall(r'Allow: (.*)|Disallow: (.*)', response)
        for match in matches:
            match = match[0] + match[1]
            if '/*/' not in match:
                url = main_url + match
                storage.add(url)
                robots.add(url)
                if '=' in url:
                    fuzzable.add(url)
        if len(matches) > 0:
            print ('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
    
    response = requester(url + '/sitemap.xml')
    
    if '<body' not in response:
        matches = findall(r'<loc>[^<]*</loc>', response)
        if matches:
            print ('%s URLs retrieved from sitemap.xml: %s' % (good, len(matches)))
            for match in matches:
                storage.add(match.split('<loc>')[1][:-6])

####
# This functions checks if the found link is crawlable or not
####

def is_link(url):
    bad = ['xml', 'png', 'bmp', 'jpg', 'jpeg', 'pdf', 'css', 'ico', 'js', 'svg', 'json']
    conclusion = False
    
    if url not in processed:
        if '.' in url[-5:]:
            extension = url[-5:].split('.')[-1]
            if extension not in bad:
                conclusion = True
            else:
                files.add(main_url + url)
        else:
            return True
    return conclusion

####
# This function extracts stuff from the response body
####

def extractor(url):
    response = requester(url)
    try:
        matches = findall(r'href=[\'"](.*?)["\']', response)
        for link in matches:
            link = link.split('#')[0]
            if is_link(link):
                if link.startswith(main_url):
                    storage.add(link)
                    if '=' in link:
                        fuzzable.add(link)
                if link.startswith('http') or link.startswith('//'):
                    if not link.startswith(main_url):
                        external.add(link)
                elif link.startswith('#') or link.startswith('javascript') or link.startswith('{{'):
                    pass
                elif link.startswith('/') and not link.startswith('//'):
                    storage.add(main_url + link)
                    if '=' in link:
                        fuzzable.add(link)
                elif not link.startswith('http') and not link.startswith('//'):
                    storage.add(main_url + '/' + link)
                    if '=' in link:
                        fuzzable.add(link)
        
        matches = findall(r'src=[\'"](.*?\.js)["\']', response)
        for match in matches:
            if match.startswith(main_url):
                scripts.add(match)
            elif match.startswith('/') and not match.startswith('//'):
                scripts.add(main_url + match)
            elif not match.startswith('http') and not match.startswith('//'):
                scripts.add(main_url + '/' + match)

        matches = findall(r'''([\w\.-]+s[\w\.-]+\.amazonaws\.com)|(github\.com/[\w\.-/]+)|(facebook\.com/.*?)[\'" ]|
(youtube\.com/.*?)[\'" ]|(linkedin\.com/.*?)[\'" ]|(twitter\.com/.*?)[\'" ]|([\w\.-]+@[\w\.-]+\.[\.\w]+)''', response)
        for match in matches:
            for x in match:
                if x != '':
                    intel.add(x)
    except:
        pass

####
# This function extracts endpoints from JavaScript Code
####

def jscanner(url):
    response = requester(url)
    matches = findall(r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]', response)
    for match in matches:
        if match[0]:
            match = match[0]
        elif match[1]:
            match = match[1]
        if not search(r'[}{><"\']', match) and not match == '/':
            endpoints.add(match)

####
# This function starts multiple threads for a function
####

def threader(function, *urls):
    threads = []
    urls = urls[0]
    for url in urls:
        task = threading.Thread(target=function, args=(url,))
        threads.append(task)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    del threads[:]

####
# This function processes the urls and sends them to "threader" function
####

def flash(function, links):
    links = list(links)
    begin = 0
    end = thread_count
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

# Step 1. Extract urls from robots.txt & sitemap.xml
zap(main_url)

# Step 2. Crawl recursively to the limit specified in "crawl_level"
for level in range(crawl_level):
    links = storage - processed
    if len(links) == 0:
        break
    if len(storage) <= len(processed):
        if len(storage) > 2 + len(seeds):
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

# Step 4. Save the results
if os.path.exists(name):
    os.system('rm -r %s' % name)
os.system('mkdir %s' % name)

with open('%s/links.txt' % name, 'w+') as f:
    for x in storage:
            f.write(x + '\n')
f.close()

with open('%s/robots.txt' % name, 'w+') as f:
    for x in storage:
            f.write(x + '\n')
f.close()

with open('%s/scripts.txt' % name, 'w+') as f:
    for x in scripts:
            f.write(x + '\n')
f.close()

with open('%s/fuzzable.txt' % name, 'w+') as f:
    for x in fuzzable:
        f.write(x + '\n')
f.close()

with open('%s/endpoints.txt' % name, 'w+') as f:
    for x in endpoints:
        f.write(x + '\n')
f.close()

with open('%s/failed.txt' % name, 'w+') as f:
    for x in failed:
        f.write(x + '\n')
f.close()

with open('%s/external.txt' % name, 'w+') as f:
    for x in external:
        f.write(x + '\n')
f.close()

with open('%s/files.txt' % name, 'w+') as f:
    for x in files:
        f.write(x + '\n')
f.close()

with open('%s/intel.txt' % name, 'w+') as f:
    for x in intel:
        f.write(x + '\n')
f.close()

print ('''%s
%s URLs: %i
%s Intel: %i
%s Files: %i
%s Endpoints: %i
%s Fuzzable URLs: %i
%s JavaScript Files: %i
%s External References: %i
%s''' % ((('%s-%s' % (red, end)) * 50), good, len(storage), good, 
len(intel), good, len(files), good, len(endpoints), good, len(fuzzable),
good, len(scripts), good, len(external),
(('%s-%s' % (red, end)) * 50)))

print ('%s Results saved in \033[;1m%s\033[0m directory' % (good, name))
