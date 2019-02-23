from __future__ import print_function
import sys
import threading

from core.colors import info

try:
    import concurrent.futures
except ImportError:
    pass


def threader(function, *urls):
    """Start multiple threads for a function."""
    threads = []
    # Because URLs is a tuple
    urls = urls[0]
    # Iterating over URLs
    for url in urls:
        task = threading.Thread(target=function, args=(url,))
        threads.append(task)
    # Start threads
    for thread in threads:
        thread.start()
    # Wait for all threads to complete their work
    for thread in threads:
        thread.join()
    # Delete threads
    del threads[:]


def flash(function, links, thread_count):
    """Process the URLs and uses a threadpool to execute a function."""
    # Convert links (set) to list
    links = list(links)
    if sys.version_info < (3, 2):
        for begin in range(0, len(links), thread_count):  # Range with step
            end = begin + thread_count
            splitted = links[begin:end]
            threader(function, splitted)
            progress = end
            if progress > len(links):  # Fix if overflow
                progress = len(links)
            print('\r%s Progress: %i/%i' % (info, progress, len(links)),
                  end='\r')
            sys.stdout.flush()
    else:
        threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers=thread_count)
        futures = (threadpool.submit(function, link) for link in links)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(links) or (i + 1) % thread_count == 0:
                print('%s Progress: %i/%i' % (info, i + 1, len(links)),
                      end='\r')
    print('')
