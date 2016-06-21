from scipy.sparse import csr_matrix
import itertools
import ujson
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
    return csr_RIV.from_sets(size, indices, values)


class csr_RIV(csr_matrix):
    def __str__(self):
        i = list(self.indices)
        d = list(self.data)
        res = list(zip(i, d))
        res.append(self.size())
        return ujson.dumps(res)

    def size(self):
        return self.shape()[1]

    def magnitude(self):
        vals = self.data
        return sum(i ** 2 for i in vals) ** 0.5

    @staticmethod
    def make(matrix):
        return csr_RIV(matrix)

    @staticmethod
    def empty(size):
        matrix = csr_matrix((1, size))
        return csr_RIV.make(matrix)

    @staticmethod
    def from_sets(size, indices, values):
        row_ind = tuple(itertools.repeat(0, times=len(indices)))
        matrix = csr_matrix((values, (row_ind, indices)), shape=(1, size))
        return csr_RIV.make(matrix)

    @staticmethod
    def to_str(riv):
        return str(riv)

    @staticmethod
    def from_str(string):
        lis = ujson.loads(string)
        size = lis.pop()
        indices = []
        values = []

        return csr_RIV.from_sets(size, indices, values)

    @staticmethod
    def sum(*rivs, size=None):
        size = size if size else rivs[0].size()
        res = csr_RIV.empty(size)
        for riv in rivs:
            res += riv
        return res

    @staticmethod
    def dot_product(riva, rivb):
        t = rivb.transpose()
        res = riva * t
        return res[0, 0]
