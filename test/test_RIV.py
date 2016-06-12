from math import sqrt
from unittest import TestCase

from riv.riv import RIV as R
from riv.vec_perms import Permutations as P
from riv.vector_element import VectorElement as V


class TestRIV(TestCase):
    test_sz = 10
    test_is = (4, 0)
    test_vs = (1, -1)

    def test_make(self):
        riv = R.make(TestRIV.test_sz,
                     (V.make(4, 1), V.make(10, -1)))
        self.assertEqual("4|1.0 10|-1.0;10", str(riv))

    def test__len(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(2, len(riv))

    def test__mult(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual("4|2 10|-2;10", str(riv * 2))

    def test__eq(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(True, riv == TestRIV.make_test_riv())
        self.assertEqual(False, riv * 2 == TestRIV.make_test_riv())

    def test__contains_int(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(True, 4 in riv)
        self.assertEqual(False, 6 in riv)

    def test__contains_velt(self):
        riv = TestRIV.make_test_riv()
        velta = V.make(4, 1)
        veltb = V.make(6, 0)
        self.assertEqual(True, velta in riv)
        self.assertEqual(False, veltb in riv)

    def test_get_point(self):
        riv = TestRIV.make_test_riv()
        vec = V.make(4, 1)
        self.assertEqual(vec, riv.__get_point__(4))

    def test__get_item_int(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(1, riv[4])
        self.assertEqual(0, riv[6])

    def test__get_item_velt(self):
        riv = TestRIV.make_test_riv()
        velta = V.make(4, 1)
        veltb = V.make(6, 2)
        self.assertEqual(1, riv[velta])
        self.assertEqual(0, riv[veltb])

    def test__add(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(riv * 2, riv + riv)

    def test__neg(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(riv * -1, -riv)

    def test__sub(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(riv * 0, riv - riv)

    def test__truediv(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(riv * 0.5, riv / 2)

    def test_from_sets(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(
            R.make(
                TestRIV.test_sz,
                (V.make(4, 1), V.make(10, -1))),
            riv)

    def test_size(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(riv.size(), 10)

    def test_points(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(
            (V.make(4, 1), V.make(10, -1)),
            riv.points())

    def test_keys(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual((4, 10), riv.keys())

    def test_vals(self):
        riv = TestRIV.make_test_riv()
        self.assertNotEqual((1, -1), riv.vals())

    def test_get_point_int(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(V.make(4, 1), riv.get_point(4))
        self.assertEqual(V.make(6, 0), riv.get_point(6))

    def test_get_point_velt(self):
        riv = TestRIV.make_test_riv()
        velt = V.make(4, 1)
        velt_2 = V.make(6, 1)
        self.assertEqual(velt, riv.get_point(velt))
        self.assertNotEqual(velt_2, riv.get_point(velt_2))

    def test_remove_zeros(self):
        riv = TestRIV.make_test_riv()
        riv_2 = R.from_sets(10, (4, 6, 10), (1, 0, -1))
        self.assertEqual(riv, riv_2.remove_zeros())

    def test_magnitude(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(sqrt(2), riv.magnitude())

    def test_normalize(self):
        riv = TestRIV.make_test_riv()
        self.assertEqual(1, riv.normalize().magnitude())

    def test_permute(self):
        perms = P.generate(10)
        riv = TestRIV.make_test_riv()
        riv_plus = riv.permute(perms, 3)
        riv_minus = riv.permute(perms, -3)
        self.assertNotEqual(riv,riv_plus)
        self.assertNotEqual(riv,riv_minus)
        self.assertNotEqual(riv_plus,riv_minus)
        self.assertEqual(riv,riv_plus.permute(perms, -3))
        self.assertEqual(riv,riv_minus.permute(perms, 3))

    @staticmethod
    def make_test_riv():
        return R.from_sets(TestRIV.test_sz,
                           TestRIV.test_is,
                           TestRIV.test_vs)
