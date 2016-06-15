'''
Created on 7 May 2016

@author: josh
'''

import random


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

    def __str__(self):
        return "permute: {}\ninverse: {}".format(self['permute'], self['invert'])

    @staticmethod
    def generate(size):
        r = random.Random()
        r.seed(0)
        permutation = list(range(size))
        r.shuffle(permutation)
        inverse = [e[0] for e in sorted(enumerate(permutation), key=lambda i: i[1])]
        return Permutations(permutation, inverse)
