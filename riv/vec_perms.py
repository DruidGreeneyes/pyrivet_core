'''
Created on 7 May 2016

@author: josh
'''

import random
import ujson


class Permutations(object):

    __slots__ = ['_parts']

    def __init__(self, permute, inverse):
        self._parts = (tuple(permute), tuple(inverse))

    def __getitem__(self, index):
        if index == 'permute' or index == 0: return self._parts[0]
        elif index == 'invert' or index == 1: return self._parts[1]
        else:
            raise IndexError("Permutation only contains entries for "
                             "'permute' and 'invert'.\n"
                             "You asked for: {}".format(index))

    def __str__(self):
        return ujson.dumps(self._parts)

    @staticmethod
    def generate(size, rand=random.Random()):
        rand.seed(0)
        permutation = list(range(size))
        rand.shuffle(permutation)
        inverse = [e[0] for e in sorted(enumerate(permutation), key=lambda i: i[1])]
        return Permutations(permutation, inverse)

    @staticmethod
    def to_str(perms):
        return str(perms)

    @staticmethod
    def from_str(string):
        perm, inv = ujson.loads(string)
        return Permutations(perm, inv)


