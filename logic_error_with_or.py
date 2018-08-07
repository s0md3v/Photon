# See https://github.com/s0md3v/Photon/issues/48

def test(url):
    return ('github.com' or 'facebook.com' or 'instagram.com' or 'youtube.com') in url


for url in ('https://www.github.com/test https://www.facebook.com/test '
            'https://www.instagram.com/test https://www.youtube.com/test').split():
    print(url, '-->', test(url))


"""
https://www.github.com/test --> True
https://www.facebook.com/test --> False
https://www.instagram.com/test --> False
https://www.youtube.com/test --> False
"""

# 'or' only delivers the first Truthy value
print('github.com' or 'facebook.com' or 'instagram.com' or 'youtube.com')

"""
github.com
"""
