"""Support for dnsdumpster.com."""
import re

import requests


def dnsdumpster(domain, output_dir):
    """Query dnsdumpster.com."""
    response = requests.Session().get('https://dnsdumpster.com/').text
    csrf_token = re.search(
        r"name='csrfmiddlewaretoken' value='(.*?)'", response).group(1)

    cookies = {'csrftoken': csrf_token}
    headers = {'Referer': 'https://dnsdumpster.com/'}
    data = {'csrfmiddlewaretoken': csrf_token, 'targetip': domain}
    response = requests.Session().post(
        'https://dnsdumpster.com/', cookies=cookies, data=data, headers=headers)

    image = requests.get('https://dnsdumpster.com/static/map/%s.png' % domain)
    if image.status_code == 200:
        with open('%s/%s.png' % (output_dir, domain), 'wb') as f:
            f.write(image.content)
