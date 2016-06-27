import itertools
import functools
import random
import ujson
import decimal


decimal.getcontext().prec = 4


def _make_values(rand, count):
    vals = itertools.repeat([1, -1], count // 2)
    vals = itertools.chain(*vals)
    vals = [decimal.Decimal(x) for x in vals]
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


class RIV(dict):
    def __init__(self, size, riv):
        super(RIV, self).__init__(riv)
        self._size = int(size)

    def __str__(self):
        return ujson.dumps((self._size, self))

    def __len__(self):
        return self._size

    def __eq__(self, riv):
        return self._size == riv._size and super(RIV, self).__eq__(riv)

    def __ne__(self, riv):
        return not self == riv

    def __missing__(self, index):
        self[index] = 0
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

    def __iadd__(self, riv):
        for (k, v) in riv.items():
            self[k] += v
        return self

    def __neg__(self):
        return RIV.make(self._size,
                        [(k, -v) for (k, v) in self.items()])

    def __sub__(self, riv):
        return self + -riv

    def __isub__(self, riv):
        print("Subtracting {} from {}".format(riv, self))
        self_items = self.items()
        items = riv.items()
        print(items)
        for (k, v) in items:
            print("key: {}".format(k))
            ov = self.__getitem__(k)
            print("old value: {}".format(ov))
            print("subtract: {}".format(v))
            nv = ov - v
            print("new value: {}".format(nv))
            self.__setitem__(k, nv)
            print("assigned: {}".format(self[k]))
        return self

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

    def count(self):
        return super(RIV, self).__len__()

    def remove_zeros(self):
        for (k, v) in list(self.items()).copy():
            if v == 0:
                del self[k]
        return self

    def magnitude(self):
        vals = self.values()
        return sum(i ** 2 for i in vals).sqrt()

    def normalize(self):
        mag = self.magnitude()
        return self / mag

    def permute(self, permutations, times):
        def permute_keys(keys, permutation):
            return [permutation[k] for k in keys]
        if times == 0: return self
        perm = (permutations['permute'] if times > 0
                else permutations['invert'])
        keys = tuple(self.keys())
        new_keys = functools.reduce(lambda ks, __: permute_keys(ks, perm),
                                    range(+times),
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
    def to_str(riv):
        return str(riv)

    @staticmethod
    def from_str(string):
        size, points = ujson.loads(string)
        points = dict((k, decimal.Decimal(v)) for (k, v) in points.items())
        return RIV.make(size, points)

    @staticmethod
    def sum(*rivs, size=None):
        size = size if size else len(rivs[0])
        res = RIV.empty(size)
        for riv in rivs:
            res += riv
        return res

    @staticmethod
    def dot_product(riva, rivb):
        res = [riva[i] * rivb[i] for i in riva if i in rivb]
        return sum(res)
