'''
Created on 7 May 2016

@author: josh
'''

from random import random


class Permutations(object):

    __slots__ = ['parts']

    def __init__(self, permute, inverse):
        self.parts = (tuple(permute), tuple(inverse))

    def __getitem__(self, index):
        if index == 'permute' or index == 0: return self.parts[0]
        elif index == 'invert' or index == 1: return self.parts[1]
        else:
            raise IndexError("Permutation only contains entries for "
                             "'permute' and 'invert'.\n"
                             "You asked for: {}".format(index))


def generate(size):
    random.seed(0)
    permutation = random.shuffle(range(size))
    inverse = (i for i, __ in sorted(enumerate(permutation), key=lambda e: e[1]))
    return Permutations(permutation, inverse)
