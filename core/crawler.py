import concurrent.futures

from core.parser import parser
from core.colors import run, info
from core.values import var, result
from core.utils import remove_regex

def crawler():
    for level in range(var['level']):
        # Links to crawl = (all links - already crawled links) - links not to crawl
        internal = result['urls']['internal']
        processed = var['processed']
        urls = remove_regex(internal - processed, var['exclude'])
        # If urls to crawl are 0 i.e. all urls have been crawled
        if not urls:
            break
        # if crawled urls are somehow more than all urls. Possible? :/
        elif len(internal) <= len(processed):
            if len(internal) > 2 + len(var['seeds']):
                break
        print('%s Level %i: %i URLs' % (run, level + 1, len(urls)))
        threadpool = concurrent.futures.ThreadPoolExecutor(
                max_workers=var['threads'])
        futures = (threadpool.submit(parser, url) for url in urls)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(urls) or (i + 1) % var['threads'] == 0:
                print('%s Progress: %i/%i' % (info, i + 1, len(urls)),
                        end='\r')
        print('')
