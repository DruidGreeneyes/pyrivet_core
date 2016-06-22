'''
Created on 7 May 2016

@author: josh
'''

import functools


def find(item, coll, default):
    return next(iter(filter(lambda x: x == item, coll)), default)


def find_index(item, sorted_coll):
    if not sorted_coll:
        return 0, False
    indices = tuple(range(len(sorted_coll)))
    length = len(indices)
    while length > 1:
        sup_index = length // 2
        index = indices[sup_index]
        current = sorted_coll[index]
        if item > current:
            indices = indices[sup_index:]
        elif item < current:
            indices = indices[:sup_index]
        else:
            return index, True
        length = len(indices)
    index = indices[0]
    current = sorted_coll[index]
    return index, item == current


def find_where(predicate, col, default):
    return next(iter(filter(predicate, col)), default)


def cached_function(func):
    def invalidate(obj):
        obj.invalid = True

    def cache_wrapper(*args, **kwargs):
        if cache_wrapper.invalid:
            cache_wrapper.cache = func(*args, **kwargs)
            cache_wrapper.invalid = False
        return cache_wrapper.cache

    cache_wrapper.invalid = True
    cache_wrapper.cache = None
    cache_wrapper.invalidate = functools.partial(invalidate, cache_wrapper)
    return cache_wrapper
