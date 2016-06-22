'''
Created on 7 May 2016

@author: josh
'''

from .dict_riv import RIV as R
from .vec_perms import Permutations as P
from random import random


def matching_keys(riva, rivb):
    return [k for k in riva if k in rivb]


def matching_vals(riva, rivb):
    return [(riva[k], rivb[k]) for k in matching_keys(riva, rivb)]


def dot_product(riva, rivb):
    return sum([a + b for (a, b) in matching_vals(riva, rivb)])


def similarity(riva, rivb):
    a = riva.normalize()
    b = rivb.normalize()
    mag = a.magnitude() * b.magnitude()
    return (dot_product(a, b) / mag) if mag else 0


def _generate_vals(count, token):
    random.seed(token)
    return random.shuffle([1 for __ in range(count // 2)] + [-1 for __ in range(count // 2)])


def _generate_indices(bound, count, token):
    random.seed(token)
    return random.sample(range(bound), count)


def generate_riv(size, nnz, token):
    return R.from_sets(size,
                       _generate_indices(size, nnz, token),
                       _generate_vals(nnz, token))


def generate_permutations (size):
    return P.generate(size)