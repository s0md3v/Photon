#!/usr/bin/env python2
import mechanize
import threading
import sys
import time
import re

white = '\033[1;97m'
green = '\033[1;32m'
red = '\033[91m'
yellow = '\033[1;33m'
end = '\033[1;m'
info = '\033[1;33m[!]\033[1;m'
que =  '\033[1;34m[?]\033[1;m'
bad = '\033[1;31m[-]\033[1;m'
good = '\033[1;32m[+]\033[1;m'
run = '\033[1;97m[~]\033[1;m'

print '''%s      ____  __          __            
     / %s__%s \/ /_  ____  / /_____  ____ 
    / %s/_/%s / __ \/ %s__%s \/ __/ %s__%s \/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\____/\__/\____/_/ /_/ \n''' % (red, white, red, white, red, white, red, white, red, white, red, white, red)

storage = set()
scripts = set()
params = set()

br = mechanize.Browser() # Just shortening the calling function
br.set_handle_robots(False) # Don't follow robots.txt
br.set_handle_equiv(True) # I don't know what it does, but its some good shit
br.set_handle_redirect(True) # Follow redirects
br.set_handle_referer(True) # Include referrer
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'),
('Accept-Encoding', 'deflate'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]

target = sys.argv[1]
name = target.split('.')[1]
storage.add(target)

def get_links(url):
    try:
        response = br.open(url).read()
        for link in br.links():
            link = link.url
            if name in link:
                if link.startswith('http'):
                    storage.add(link)
                    if '=' in link:
                        params.add(link)
                elif link.startswith('/'):
                    storage.add(target + link)
                    if '=' in link:
                        params.add(link)
                else:
                    storage.add(target + '/' + link)
                    if '=' in link:
                        params.add(link)
        matches = re.findall(r'src=[\'"][^<]*\.js', response)
        for match in matches:
            if 'http' in match:
                scripts.add(match[5:])
            elif match[5:].startswith('/'):
                scripts.add(url + match[5:])
            else:
                scripts.add(url + '/' + match[5:])
    except:
        storage.remove(url)

def initiate():
    database = list(storage.copy())
    def part1():
        for url in database[:len(storage)/2]:
            time.sleep(1.5)
            get_links(url)
    def part2():
        for url in database[len(storage)/2:]:
            time.sleep(1.5)
            get_links(url)
    t1 = threading.Thread(target=part1) #Calls the part1 function via a thread
    t2 = threading.Thread(target=part2) #Calls the part2 function via a thread
    t1.start() #starts thread 1
    t2.start() #starts thread 2
    t1.join() #Joins both
    t2.join() #of the threads

get_links(target)
print '%s URLs to crawl: %i' % (info, len(storage))
approx = (len(storage)/20)
if approx > 0:
    print '%s Time required: ~%i minutes' % (info, approx)
else:
    print '%s Time required: ~1 minute' % info
initiate()

print '%s-%s' % (red, end) * 60

print '%s URLs found: %i' % (info, len(storage))
for x in storage:
    print x

print '%s-%s' % (red, end) * 60

print '%s JavaScript files found:' % info
for x in scripts:
    print x

print '%s-%s' % (red, end) * 60

print '%s Fuzzable URLs found:' % info
for x in params:
    print x

choice = raw_input('Would you like to save the results? [Y/n]').lower()
if choice != 'n':
    with open('%s-links.txt' % name, 'w+') as f:
        for x in storage:
            f.write(x + '\n')

    with open('%s-js.txt' % name, 'w+') as f:
        for x in scripts:
            f.write(x + '\n')

    with open('%s-fuzzable.txt' % name, 'w+') as f:
        for x in params:
            f.write(x + '\n')