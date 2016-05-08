'''
Created on 7 May 2016

@author: josh
'''

def find(item, coll, default):
    return next(iter(filter(lambda x: x == item, coll)), default)

def find_where(predicate, col, default):
    return next(iter(filter(predicate, col)), default)