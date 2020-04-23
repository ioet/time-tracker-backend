import re

def remove_none_values(dictionary):
    dictionary_with_values = {}
    for key, value in dictionary.items():
        if value is not None:
            dictionary_with_values.update({key: value})
    return dictionary_with_values


def remove_filters_wrapper_from_keys(dictionary):
    dictionary_with_unwrapped_keys = {}
    for key, value in dictionary.items():
        unwrapped_key = re.search('\\[(.+?)\\]', key).groups()[0]
        dictionary_with_unwrapped_keys.update({unwrapped_key: value})
    return dictionary_with_unwrapped_keys
