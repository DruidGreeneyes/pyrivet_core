'''
Created on 7 May 2016

@author: josh
'''

# Random Index Vector
# random-access tuple of vector_elements
# used to represent a compressed sparse vector.
# indices whose value is zero don't exist.

import labels.vector_element as vec_elt
from util import find_where
from multipledispatch import dispatch


class RIV(object):

    __slots__ = ['parts']

    def __init__(self, size, points):
        self.parts = (size, tuple(points))

    def __str__(self):
        return "{};{}".format(" ".join(map(str, self.points())), self.size)

    def __len__(self):
        return len(self.points())
    
    def __eq__(self, riv):
        return self.size() == riv.size() and self.points() == riv.points()
    
    @dispatch(int)
    def __contains__(self, index):
        return index in self.keys()

    @dispatch(vec_elt.VectorElement)
    def __contains__(self, v_elt):
        return self.__contains__(v_elt['index'])

    def __get_point__(self, index):
        if 0 < index < self.size():
            return find_where(lambda v: v.index() == index,
                              self.points(),
                              vec_elt.from_index(index))
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(index))

    @dispatch(int)
    def __getitem__(self, index):
        return self.__get_point__(index)['value']

    @dispatch(vec_elt.VectorElement)
    def __getitem__(self, v_elt):
        return self.__getitem__(v_elt['index'])
    
    def __iter__(self): return iter(self.points())

    def __add__(self, riv):
        pointsb = map(lambda v:
                        v + self[v.__index__()]
                        if v['index'] in self
                        else v,
                      riv.points())
        return make(self.size(),
                    set(self.points()).difference(pointsb).union(pointsb)).remove_zeros()

    def __neg__(self):
        return make(self.size(),
                    (-v for v in self))

    def __sub__(self, riv): return self + -riv

    def __mul__(self, scalar):
        return make(self.size(),
                    (v * scalar for v in self))

    def __truediv__(self, scalar):
        return make(self.size(),
                    (v / scalar for v in self))

    def size(self): return self.parts[0]

    def points(self): return self.parts[1]

    def keys(self): return (v['index'] for v in self)

    def vals(self): return (v['value'] for v in self)

    @dispatch(int)
    def get_point(self, index): return self.__get_point__(index)

    @dispatch(vec_elt.VectorElement)
    def get_point(self, v_elt): return self.get_point(v_elt['index'])

    def remove_zeros(self):
        return make(self.size(),
                    (v for v in self if v['value'] != 0))

    def magnitude(self):
        return sum(i * i for i in self.vals()) ** 0.5

    def normalize(self): return self / self.magnitude()

    def permute(self, permutations, times):
        if not times:
            return self
        else:
            keys = self.keys()
            p = 0 if times > 0 else 1
            for __ in range(abs(times)):
                keys = [permutations[p][i] for i in keys]
            return from_sets(self.size(), keys, self.vals())


def make(size, points): return RIV(size, points)


def empty(size): return make(size, ())


def from_sets(size, indices, values):
    l = len(indices)
    if l == len(values):
        return make(size,
                    map(lambda x: vec_elt.make(indices[x], values[x]),
                        range(l)))
    else:
        raise IndexError("Set lengths do not match: {} != {}".format(l, len(values)))


def from_str(string):
    points_string, size = string.split(";")
    return make(size, map(vec_elt.from_str, points_string.split(" ")))