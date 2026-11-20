"""Support for dnsdumpster.com."""
import re

import requests


def dnsdumpster(domain, output_dir):
    """Query dnsdumpster.com."""
    headers = {'Referer': 'https://dnsdumpster.com/'}
    data = {'target': domain}
    response = requests.post('https://dnsdumpster.com/htmld/', data=data, headers=headers)

    match = re.search(r"/dl/maps/"+domain+"-([0-9a-f-]+)", response.text)
    file_hash = match.group(1)
    image = requests.get('https://dnsdumpster.com/dl/maps/%s-%s.png' % (domain, file_hash))
    if image.status_code == 200:
        with open('%s/%s.png' % (output_dir, domain), 'wb') as f:
            f.write(image.content)
