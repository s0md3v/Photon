import os
import sys
import time
import velocity
import warnings
import argparse

from core.zap import zap
from core.crawler import crawler
from core.values import var, result
from core.load_modules import load_modules
from core.colors import red, end, bad, good, info, white
from core.utils import get_tld, stabilize, writer, timer, is_token

# Processing command line arguments
parser = argparse.ArgumentParser()
# Options
parser.add_argument('--headers', help='HTTP headers', dest='headers')
parser.add_argument('--cookie', help='HTTP cookie value', dest='cookie')
parser.add_argument('-u', '--url', help='starting point', dest='input_url')
parser.add_argument('-m', '--modules', help='modules to use', dest='modules', nargs="+")
parser.add_argument('-s', '--seeds', help='additional seed URLs', dest='seeds', nargs="+", default=[])
parser.add_argument('--timeout', help='http request timeout', dest='timeout', type=float, default=15)
parser.add_argument('--exclude', help='exclude urls matching this regex', dest='exclude')
parser.add_argument('--include', help='only crawl urls matching this regex', dest='include')
parser.add_argument('-l', '--level', help='levels to crawl', dest='level', type=int, default=3)
parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=int, default=0)
parser.add_argument('-t', '--threads', help='maximum concurrent requests', dest='threads', type=int, default=2)
parser.add_argument('--user-agent', help='custom user agent', dest='user_agent', default='https://github.com/s0md3v/Photon')
# Switches
parser.add_argument('--wide', help='domain wide crawling', dest='wide', action='store_true')
parser.add_argument('-v', '--verbose', help='verbose output', dest='verbose', action='store_true')
parser.add_argument('--gentle', help='minimal load on target', dest='gentle', action='store_true')
parser.add_argument('--random-agent', help='use a random user agent', dest='random_agent', action='store_true')
parser.add_argument('--as-google', help='crawl the website as google crawler', dest='as_google', action='store_true')

args = parser.parse_args() # Parse the supplied arguments as a namespace object
args_dict = vars(args) # Convert the namespace object to a dict

for argument in args_dict: # iterate overt the namespace dict
    var[argument] = args_dict[argument] # update global variables

print('''%s      ____  __          __
     / %s__%s \\/ /_  ____  / /_____  ____
    / %s/_/%s / __ \\/ %s__%s \\/ __/ %s__%s \\/ __ \\
   / ____/ / / / %s/_/%s / /_/ %s/_/%s / / / /
  /_/   /_/ /_/\\____/\\__/\\____/_/ /_/ %sv2.0%s\n''' %
      (red, white, red, white, red, white, red, white, red, white, red, white,
       red, white, end))

try:
    from urllib.parse import urlparse  # For Python 3
except ImportError:
    print('%s Photon runs only on Python 3.2 and above.', bad)
    quit()

then = time.time() # record starting time

# Disable SSL related warnings
warnings.filterwarnings('ignore')
var['path'] = sys.path[0]
if not var['input_url'].startswith('http'):
    var['input_url'] = stabilize(args.input_url) # update input_url when http(s) isn't present

if var['wide']:
    var['scope'] = get_tld(var['input_url'])
else:
    var['scope'] = urlparse(var['input_url']).netloc

if var['gentle']:
    var['threads'] = 1
    var['delay'] = 1
if var['delay']:
    var['threads'] = 1

if var['random_agent']:
    with open(var['path'] + '/db/user_agents.txt', 'r') as uas:
        var['user_agents'] = [agent.strip('\n') for agent in uas]

result['urls']['internal'] = set(args.seeds)
load_modules('before-crawling')
parsed_url = urlparse(var['input_url'])
root_url = parsed_url.scheme + '://' + parsed_url.netloc
var['root_url'] =  root_url
result['urls']['internal'].add(var['root_url'])
zap() # parse sitemap.xml and robots.txt

try:
    crawler()
except KeyboardInterrupt:
    print('%s Crawler stopped' % info)

now = time.time() # record ending time
diff = (now - then) # total time taken
minutes, seconds, time_per_request = timer(diff, var['processed'])

result['data']['files'] = list(result['data']['files'])
result['urls']['failed'] = list(result['urls']['failed'])
result['data']['websites'] = list(result['data']['websites'])
result['urls']['internal'] = list(result['urls']['internal'])
result['urls']['external'] = list(result['urls']['external'])
result['urls']['fuzzable'] = list(result['urls']['fuzzable'])

if 'token' in result['data']['extractors']:
    valid_tokens = {}
    for token, url in result['data']['extractors']['token'].items():
        is_valid = is_token(token)
        if is_valid:
            valid_tokens[token] = url
    result['data']['extractors']['token'] = valid_tokens


module_count = 0
for module in result['modules']:
    module_count += len(module)

print(red + ('-' * 60) + end)
print('%s Files: %i' % (good, len(result['data']['files'])))
print('%s Websites: %i' % (good, len(result['data']['websites'])))
print('%s Internal: %i' % (good, len(result['urls']['internal'])))
print('%s External: %i' % (good, len(result['urls']['external'])))
print('%s Fuzzable: %i' % (good, len(result['urls']['fuzzable'])))
print('%s From modules: %i' % (good, module_count))
print(red + ('-' * 60) + end)
print('%s Total requests made: %i' % (info, len(var['processed'])))
print('%s Total time taken: %i minutes %i seconds' % (info, minutes, seconds))
print('%s Requests per second: %i' % (info, time_per_request))

output_dir = var['scope']

if not os.path.exists(output_dir): # if the directory doesn't exist
    os.mkdir(output_dir) # create a new directory

load_modules('after-crawling')

for key, value in result.items():
    writer(value, sys.path[0] + '/' + output_dir + '/' + key + '.json')
