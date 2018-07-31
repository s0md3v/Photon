import re
import requests
from tld import get_fld

def dnsdumpster(domain, output_dir, colors):
    if colors:
        run = '\033[1;97m[~]\033[1;m'
    else:
        run = ''
    print ('%s Retrieving DNS related data' % run)
    response = requests.Session().get('https://dnsdumpster.com/').text
    csrf_token = re.search(r"name='csrfmiddlewaretoken' value='(.*?)'", response).group(1)

    cookies = {'csrftoken': csrf_token}
    headers = {'Referer': 'https://dnsdumpster.com/'}
    data = {'csrfmiddlewaretoken': csrf_token, 'targetip': domain}
    response = requests.Session().post('https://dnsdumpster.com/', cookies=cookies, data=data, headers=headers)

    image = requests.get('https://dnsdumpster.com/static/map/%s.png' % get_fld(domain, fix_protocol=True))
    if image.status_code == 200:
        with open('%s/%s.png' % (output_dir, domain), 'wb') as f:
            f.write(image.content)
    else:
        print ('%s Failed to retrieve DNS image' % run)
