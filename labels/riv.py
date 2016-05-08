'''
Created on 7 May 2016

@author: josh
'''

# Random Index Vector
# random-access tuple of vector_elements
# used to represent a compressed sparse vector.
# indices whose value is zero don't exist.

import labels.vector_element as v_elt
from util import find_where

class RIV(object):
    # 

    __slots__ = ['parts']

    def __init__(self, size, points):
        self.parts = (size, dict(points))

    def __str__(self):
        return "{};{}".format(" ".join(map(str, self.points)), self.size)

    def __len__(self):
        return len(self.points)
    
    def __eq__(self, riv):
        return self.size() == riv.size() and self.points() == riv.points()
    
    def __contains__(self, index):
        return index in self.keys()
    
    def __getitem__(self, index):
        return self.points[index]
    
    def __missing__(self, index):
        return v_elt.from_index(index)
    
    def __iter__(self):
        return iter(self.points)
    
    def __add__(self, riv):
        pointsb = map(lambda v:
                        v  + self[v.__index__()]
                        if v['index'] in self
                        else v,
                      riv.points())
        return make(self.size(),
                    self.points().difference(pointsb).union(pointsb))

    def size(self): return self.parts[0]
    def points(self): return self.parts[1]

    def keys(self): return map(lambda v: v['index'], self.points())

    def vals(self): return map(lambda v: v['index'], self.points())

    def contains_index(self, index): return index in self.keys()
   
    def contains_elt(self, v_elt): return v_elt in self.points()

    def get_point(self, index):
        if 0 < index < self.size():
            return find_where(lambda v: v.index() == index,
                              self.points(),
                              v_elt.from_index(index))
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(index))
    
    def get(self, v_elt):
        return self.get_point(v_elt.index()).value()
    
    def add(self, other):
        pointsb = map(lambda v: v if not self.contains_elt(v) else v.add_value(self.get(v)),
                      other.points())
        return make(self.size(),
                    set(self.points()).difference(pointsb).union(pointsb))
    
    def add_point(self, v_elt):
        if 0 < v_elt.index() < self.size:
            return make(self.size(),
                        dict(self.points()).update(v_elt + (self.get(v_elt))))
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(v_elt.index()))
    
    def negate(self):
        return make(self.size(),
                    -elt for elt in self.points())
    
    def subtract(self, other): return self.add(other.negate())
    
    def subtract_point(self, v_elt): return self.add_point(v_elt.negate)
    
    def multiply(self, scalar):
        return make(self.size(),
                    map(lambda v: v.multiply(scalar),
                        self.points()))
    
    def divide_by(self, scalar):
        return make(self.size(),
                    map(lambda v: v.divide_by(scalar),
                        self.points()))

def make(size, points): return RIV(size, points)

def empty(size): return make(size, ())

def from_sets(size, indices, values):
    l = len(indices)
    if l == len(values):
        return make(size,
                    map(lambda x: v_elt.make(indices[x], values[x]),
                        range(l)))
    else:
        raise IndexError("Set lengths do not match: {} != {}".format(l, len(values)))

def from_str(string):
    points_string, size = string.split(";")
    return make(map(v_elt.from_str, points_string.split(" ")), size)