import itertools
import functools
import random
import ujson


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
    return RIV.make(size, indices, values)


class RIV(object):
    def __init__(self, size, indices, values):
        self._size = int(size)
        self._indices = list(indices)
        self._values = list(map(float, values))

    def __str__(self):
        points = list(zip(self._indices, self._values))
        points.append(self._size)
        return ujson.dumps(points)

    def __len__(self):
        return self._size

    def __eq__(self, riv):
        points = self.points()
        other_points = riv.points()
        return (self._size == riv._size and
                points == other_points)

    def __ne__(self, riv):
        return not self == riv

    def __contains__(self, index):
        return index in self._indices

    def _get_index(self, index):
        try:
            i = self._indices.index(index)
            return i
        except ValueError:
            return None

    def __getitem__(self, index):
        i = self._get_index(index)
        if i is None:
            return 0
        else:
            return self._values[i]

    def _add_item(self, index, value):
        i = self._get_index(index)
        if i is None:
            self._indices.append(index)
            self._values.append(value)
        else:
            self._values[i] += value

    def __add__(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        res = self.copy()
        for i, v in riv.points():
            res._add_item(i, v)
        return res

    def __iadd__(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        for i, v in riv.points():
            self._add_item(i, v)
        return self

    def __sub__(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        res = self.copy()
        for i, v in riv.points():
            res._add_item(i, -v)
        return res

    def __isub__(self, riv):
        if self._size != riv._size:
            raise IndexError("Cannot add or subtract rivs of different sizes:\n"
                             "self: {} != riv: {}".format(len(self), len(riv)))
        for i, v in riv.points():
            self._add_item(i, -v)
        return self

    def __mul__(self, scalar):
        return RIV(
            self._size,
            self._indices,
            [v * scalar for v in self._values]
        )

    def __imul__(self, scalar):
        self._values = [v * scalar for v in self._values]
        return self

    def __truediv__(self, scalar):
        return self * (1 / scalar)

    def __idiv__(self, scalar):
        self *= (1 / scalar)
        return self

    def __neg__(self):
        return self * -1

    def copy(self):
        return RIV(self._size,
                   self._indices.copy(),
                   self._values.copy())

    def points(self):
        return tuple(sorted(zip(self._indices, self._values)))

    def count(self):
        return len(self._indices)

    def remove_zeros(self):
        points = self.points()
        points = filter(lambda e: round(e[1], 6) != 0, points)
        return RIV.from_points(self._size, points)

    def destructive_sum(self, *rivs):
        for riv in rivs:
            self += riv
        return self.remove_zeros()

    def magnitude(self):
        return sum(v ** 2 for v in self._values) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        return self / mag

    def permute(self, permutations, times):
        def permute_keys(keys, permutation):
            return [permutation[k] for k in keys]
        if times == 0: return self
        perm = permutations['permute'] if times > 0 else permutations['invert']
        keys = self._indices.copy()
        keys = functools.reduce(lambda ks, __: permute_keys(ks, perm),
                                range(+times),
                                keys)
        return RIV.make(self._size,
                        keys,
                        self._values)

    @staticmethod
    def make(size, indices, values):
        return RIV(size, indices, values)

    @staticmethod
    def to_str(riv):
        return str(riv)

    @staticmethod
    def from_points(size, points):
        indices = []
        values = []
        for (i, v) in points:
            indices.append(i)
            values.append(v)
        return RIV.make(size, indices, values)

    @staticmethod
    def from_str(string):
        points = ujson.loads(string)
        size = points.pop()
        return RIV.from_points(size, points)

    @staticmethod
    def empty(size):
        return RIV.make(size, [], [])

    @staticmethod
    def sum(*rivs, size=None):
        size = size if size else len(rivs[0])
        res = RIV.empty(size)
        return res.destructive_sum(*rivs)

    @staticmethod
    def dot_product(riva, rivb):
        indices = set(riva._indices).intersection(rivb._indices)
        res = 0.0
        for i in indices:
            res += riva[i] * rivb[i]
        return res
