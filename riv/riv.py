'''
Created on 7 May 2016

@author: josh
'''

# Random Index Vector
# random-access tuple of vector_elements
# used to represent a compressed sparse vector.
# indices whose value is zero don't exist.

import itertools as IT

from riv.vector_element import VectorElement as V
from util import find_where
from multipledispatch import dispatch


class RIV(object):

    __slots__ = ['_parts']

    def __init__(self, size, points):
        self._parts = (size, tuple(points))

    def __str__(self):
        return "{};{}".format(" ".join(map(str, self.points())), len(self))

    def __len__(self):
        return self._parts[0]
    
    def __eq__(self, riv):
        return len(self) == riv.size() and self.points() == riv.points()
    
    @dispatch(int)
    def __contains__(self, index):
        return index in self.keys()

    @dispatch(V)
    def __contains__(self, v_elt):
        return self.__contains__(v_elt['index'])

    def __get_point__(self, index):
        if 0 <= index < len(self):
            return find_where(lambda v: v['index'] == index,
                              self.points(),
                              V.from_index(index))
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(index))

    @dispatch(int)
    def __getitem__(self, index):
        return self.__get_point__(index)['value']

    @dispatch(V)
    def __getitem__(self, v_elt):
        return self[(v_elt['index'])]
    
    def __iter__(self): return iter(self.points())

    def __add__(self, riv):
        adds = map(lambda v: self[v] + riv[v],
                   frozenset(self.points()).intersection(riv.points()))
        others = frozenset(self.points()).symmetric_difference(riv.points())
        return RIV.make(len(self),
                        IT.chain(filter(lambda v: v.is_not_zero(),
                                        adds),
                                 others))

    def __neg__(self):
        return RIV.make(len(self),
                        (-v for v in self))

    def __sub__(self, riv): return self + -riv

    def __mul__(self, scalar):
        return RIV.make(len(self),
                        (v * scalar for v in self))

    def __truediv__(self, scalar):
        return RIV.make(len(self),
                        (v / scalar for v in self))

    def count(self): return self._parts[0]

    def points(self): return self._parts[1]

    def keys(self): return (v['index'] for v in self)

    def vals(self): return (v['value'] for v in self)

    @dispatch(int)
    def get_point(self, index): return self.__get_point__(index)

    @dispatch(V)
    def get_point(self, v_elt): return self.get_point(v_elt['index'])

    def remove_zeros(self):
        return RIV.make(len(self),
                        filter(lambda v: v.is_not_zero(),
                               self.points()))

    def magnitude(self):
        return sum(i * i for i in self.vals()) ** 0.5

    def normalize(self): return self.__truediv__(self.magnitude())

    def permute(self, permutations, times):
        if not times:
            return self
        else:
            keys = self.keys()
            p = 0 if times > 0 else 1
            for __ in range(abs(times)):
                keys = [permutations[p][i] for i in keys]
            return RIV.from_sets(len(self), keys, self.vals())

    @staticmethod
    def make(size, points): return RIV(size, points)

    @staticmethod
    def empty(size): return RIV.make(size, ())

    @staticmethod
    def from_sets(size, indices, values):
        l = len(indices)
        if l == len(values):
            return RIV.make(size,
                            map(lambda x: V.make(indices[x], values[x]),
                                range(l)))
        else:
            raise IndexError("Set lengths do not match: {} != {}".format(l, len(values)))

    @staticmethod
    def from_str(string):
        points_string, size = string.split(";")
        return RIV.make(size, map(V.from_str, points_string.split(" ")))