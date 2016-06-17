import itertools
import functools
import random


def _make_values(rand, count):
    vals = list(itertools.repeat([1, -1], count // 2))
    vals = list(itertools.chain(*vals))
    rand.shuffle(vals)
    return tuple(vals)


def _make_indices(rand, size, count):
    inds = set()
    while len(inds) < count:
        inds.add(rand.randint(0, size - 1))
    return tuple(inds)


def generate_riv(size, nnz, token, rand=None):
    nnz = nnz if nnz % 2 == 0 else nnz + 1
    r = rand if rand else random.Random()
    r.seed(token)
    indices = _make_indices(r, size, nnz)
    values = _make_values(r, nnz)
    return RIV.from_sets(size, indices, values)


def _str_item(dict_item):
    k, v = dict_item
    return "{}|{}".format(k, v)


class RIV(dict):

    def __init__(self, size, riv):
        super(RIV, self).__init__(riv)
        self._size = int(size)

    def __str__(self):
        points = sorted(self.items())
        points = map(_str_item, points)
        return "{};{}".format(" ".join(points), self._size)

    def __len__(self):
        return self._size

    def __eq__(self, riv):
        return self._size == riv._size and super(RIV, self).__eq__(riv)

    def __ne__(self, riv):
        return not self == riv

    def __getitem__(self, index):
        if 0 <= index < self._size:
            return super(RIV, self).__getitem__(index)
        else:
            raise IndexError("Index is beyond the scope of this riv: {}".format(index))

    def __missing__(self, __):
        return 0

    def __add__(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        new = RIV.empty(self._size)
        points = itertools.chain(self.items(), riv.items())
        for (i, v) in points:
            new[i] += v
        return new

    def __neg__(self):
        return RIV.make(self._size,
                        [(k, -v) for (k, v) in self.items()])

    def __sub__(self, riv):
        return self + -riv

    def __mul__(self, scalar):
        return RIV.make(self._size,
                        [(k, v * scalar) for (k, v) in self.items()])

    def __truediv__(self, scalar):
        return RIV.make(self._size,
                        [(k, v / scalar) for (k, v) in self.items()])

    def keys(self):
        return tuple(super(RIV, self).keys())

    def vals(self):
        return tuple(super(RIV, self).values())

    def destructive_add(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(self._size, riv._size))
        for (k, v) in riv.items():
            self[k] += v
        return self

    def destructive_subtract(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(self._size, riv._size))
        for (k, v) in riv.items():
            self[k] -= v
        return self

    def count(self):
        return super(RIV, self).__len__()

    def remove_zeros(self):
        for (k, v) in list(self.items()).copy():
            if round(v, 6) == 0:
                del self[k]
        return self

    def magnitude(self):
        vals = self.values()
        return sum(i ** 2 for i in vals) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        return self.__truediv__(mag)

    def permute(self, permutations, times):
        def permute_keys(keys, permutation):
            return [permutation[k] for k in keys]
        perm = (permutations['permute'] if times > 0
                else permutations['invert'])
        keys = tuple(self.keys())
        new_keys = functools.reduce(lambda ks, __: permute_keys(ks, perm),
                                    range(abs(times)),
                                    keys)
        return RIV.from_sets(len(self), new_keys, self.values())

    @staticmethod
    def make(size, riv):
        return RIV(size, riv)

    @staticmethod
    def from_sets(size, keys, vals):
        return RIV(size, dict(zip(keys, vals)))

    @staticmethod
    def empty(size):
        return RIV(size, dict())

    @staticmethod
    def from_str(string):
        points, size = string.split(";")
        points = points.split(" ")
        points = [p.split("|") for p in points]
        points = [(int(k), int(v)) for [k, v] in points]
        return RIV.make(size, points)

    @staticmethod
    def sum_rivs(*rivs, size=None):
        t_rivs = tuple(rivs)
        size = size if size else len(t_rivs[0])
        empty_riv = RIV.empty(size)
        res = functools.reduce(lambda i, v: i.destructive_add(v),
                               t_rivs,
                               empty_riv)
        return res
