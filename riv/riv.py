'''
Created on 7 May 2016

@author: josh
'''

# Random Index Vector
# random-access tuple of vector_elements
# used to represent a compressed sparse vector.
# indices whose value is zero don't exist.

from riv.vector_element import VectorElement as V
import functools as FT
import itertools as IT
from util import find_where
from multipledispatch import dispatch
import random


class RIV(object):

    def __init__(self, size, points):
        self._parts = (int(size), tuple(sorted(points)))

    def __str__(self):
        return "{};{}".format(" ".join(map(str, self.remove_zeros())),
                              len(self))

    def __len__(self):
        return self._parts[0]
    
    def __eq__(self, riv):
        if self is riv:
            return True
        elif len(self) == len(riv):
            if (False not in
                    (self[v].strict_equals(riv[v]) for v in set(self).union(riv))):
                return True
        return False

    def __ne__(self, riv):
        return not self == riv
    
    @dispatch(int)
    def __contains__(self, index):
        return index in self.keys()

    @dispatch(V)
    def __contains__(self, v_elt):
        return self.__contains__(v_elt['index'])

    @dispatch(int)
    def __getitem__(self, index):
        if 0 <= index < len(self):
            return find_where(lambda v: v == index,
                              self,
                              V.partial(index))
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(index))

    @dispatch(V)
    def __getitem__(self, v_elt):
        return self[(v_elt['index'])]
    
    def __iter__(self): return iter(self.points())

    def __add__(self, riv):
        if len(self) != len(riv):
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        points = (self[v] + riv[v] if (v in self and v in riv) else v
                  for v in set(self).union(riv))
        return RIV.make(len(self), points)

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

    def points(self): return self._parts[1]

    def count(self):
        return len(self.remove_zeros().points())

    def keys(self): return tuple(v['index'] for v in self)

    def vals(self): return tuple(v['value'] for v in self)

    @dispatch(int)
    def get_point(self, index): return self[index]

    @dispatch(V)
    def get_point(self, v_elt): return self[v_elt]

    def remove_zeros(self):
        return RIV.make(len(self),
                        filter(lambda v: v.not_zero(),
                               self))

    def magnitude(self):
        return sum(i * i for i in self.vals()) ** 0.5

    def normalize(self): return self.__truediv__(self.magnitude())

    def permute(self, permutations, times):
        def permute_keys(keys, permutation):
            return [permutation[k] for k in keys]
        perm = (permutations['permute'] if times > 0
                else permutations['invert'])
        new_keys = FT.reduce(
            lambda ks, __: permute_keys(ks, perm),
            range(abs(times)),
            self.keys())
        return RIV.from_sets(len(self), new_keys, self.vals())

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
        return RIV.make(size, [V.from_str(s) for s in points_string.split(" ")])

    @staticmethod
    def _make_values(rand, count):
        vals = FT.reduce(lambda i, x: i + x,
                         IT.repeat([1, -1], count // 2))

        rand.shuffle(vals)
        return tuple(vals)

    @staticmethod
    def _make_indices(rand, size, count):
        inds = set()
        while len(inds) < count:
            inds.add(rand.randint(0, size - 1))
        return tuple(inds)

    @staticmethod
    def generate_riv(size, nnz, token):
        assert nnz % 2 == 0, "nnz must be even, otherwise num -1s != num 1s"
        r = random.Random()
        r.seed(token)
        return RIV.from_sets(size,
                             RIV._make_indices(r, size, nnz),
                             RIV._make_values(r, nnz))
