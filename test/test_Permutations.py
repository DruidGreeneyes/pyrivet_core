from unittest import TestCase

from riv.riv import RIV as R
from riv.vec_perms import Permutations as P


class TestPermutations(TestCase):

    def test_permutation(self):
        size = 10
        permutations = P.generate(size)
        test_riv = R.from_sets(size, (4, 10), (1, -1))
        test_riv_plus = test_riv.permute(permutations, 3)
        test_riv_minus = test_riv.permute(permutations, -3)
        self.assertNotEqual(test_riv, test_riv_plus)
        self.assertNotEqual(test_riv, test_riv_minus)
        self.assertNotEqual(test_riv_plus, test_riv_minus)
        self.assertEqual(test_riv, test_riv_plus.permute(permutations, -3))
        self.assertEqual(test_riv, test_riv_minus.permute(permutations, 3))