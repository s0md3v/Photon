import os


def mirror(url, response):
    if response != 'dummy':
        clean_url = url.replace('http://', '').replace('https://', '').rstrip('/')
        parts = clean_url.split('?')[0].split('/')
        root = parts[0]
        webpage = parts[-1]
        parts.remove(root)
        try:
            parts.remove(webpage)
        except ValueError:
            pass
        prefix = root + '_mirror'
        try:
            os.mkdir(prefix)
        except OSError:
            pass
        suffix = ''
        if parts:
            for directory in parts:
                suffix += directory + '/'
                try:
                    os.mkdir(prefix + '/' + suffix)
                except OSError:
                    pass
        path = prefix + '/' + suffix
        trail = ''
        if '.' not in webpage:
            trail += '.html'
        if webpage == root:
            name = 'index.html'
        else:
            name = webpage
        if len(url.split('?')) > 1:
            trail += '?' + url.split('?')[1]
        with open(path + name + trail, 'w+') as out_file:
            out_file.write(response.encode('utf-8'))
