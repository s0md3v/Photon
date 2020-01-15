import sys
import json

def loader(path):
    with open(path, 'r') as f:
        result = [line.rstrip('\n').encode('utf-8').decode('utf-8') for line in f]
    return '\n'.join(result)

config = json.loads(loader(sys.path[0] + '/db/config.json'))

var = {'processed':set()} # I would have used 'vars' but Python already uses it

result = {}
result['urls'] = {}
result['data'] = {}
result['modules'] = {}
result['data']['files'] = set()
result['urls']['failed'] = set()
result['data']['extractors'] = {}
result['data']['websites'] = set()
result['urls']['internal'] = set()
result['urls']['external'] = set()
result['urls']['fuzzable'] = set()
result['urls']['disallowed'] = set()
