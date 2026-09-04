import extruct


def extract_metadata(text, url):
    """Extract all metadata present in the page and return a dictionary of metadata lists. 
    
    Args:
        url (string): URL of page from which to extract metadata. 
    
    Returns: 
        metadata (dict): Dictionary of json-ld, microdata, and opengraph lists. 
        Each of the lists present within the dictionary contains multiple dictionaries.
    """
    
    metadata = extruct.extract(text, 
                               base_url=url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])
    return metadata


def get_dictionary_by_key_value(dictionary, target_key, target_value):
    """Return a dictionary that contains a target key value pair. 
    
    Args:
        dictionary: Metadata dictionary containing lists of other dictionaries.
        target_key: Target key to search for within a dictionary inside a list. 
        target_value: Target value to search for within a dictionary inside a list. 
    
    Returns:
        target_dictionary: Target dictionary that contains target key value pair. 
    """
    result = None
    for key in dictionary:
        if len(dictionary[key]) > 0:
            for item in dictionary[key]:
                if item[target_key] == target_value:
                    return item
    return result


def get_dictionary_by_key(dictionary, target_key):
    """Return a dictionary that contains a target key. 
    
    Args:
        dictionary: Metadata dictionary containing lists of other dictionaries.
        target_key: Target key to search for within a dictionary inside a list. 
    
    Returns:
        target_dictionary: Target dictionary that contains target key value pair. 
    """
    result = None
    for key in dictionary:
        if len(dictionary[key]) > 0:
            for item in dictionary[key]:
                if item[target_key]:
                    return item
    return result