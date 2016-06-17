from riv.dict_riv import RIV
import riv.dict_riv as riv
from riv.vec_perms import Permutations as P
import pytest
import random


def test_riv():
    test_key_a = 4
    test_key_b = 0
    test_val_a = 1
    test_val_b = -1
    test_size = 100
    test_elt_a = (test_key_a, test_val_a)
    test_elt_b = (test_key_b, test_val_b)
    test_points = dict((test_elt_a, test_elt_b))
    test_is = tuple(test_points.keys())
    test_vs = tuple(test_points.values())
    test_str_points = ["{}|{}".format(k, v) for k, v in sorted(test_points.items())]
    test_str = "{};{}".format(
        " ".join(test_str_points),
        test_size)
    test_perms = P.generate(test_size)
    test_permutation_factor = random.Random().randint(-10000, 10000)

    def generate_bad_key():
        return random.Random().choice(
            [i for i in range(test_size) if i not in test_is])
    bad_key = generate_bad_key()

    points_riv = RIV.make(test_size, test_points)
    assert test_str == str(points_riv), \
        ("RIV.make() or RIV.__str__() seems to have failed. These two should be equal:\n"
         "{} != {}").format(test_str, points_riv)

    def make_test_riv(inc=1):
        # Genrate a quick test riv where the vals are all inc or -inc
        return RIV.from_sets(test_size,
                             test_is,
                             [v * inc for v in test_vs])

    test_riv_1 = make_test_riv(1)
    assert points_riv == test_riv_1, \
        ("RIV.from_sets() has failed. These two should be equal:\n"
         "{} != {}").format(points_riv, test_riv_1)

    assert test_size == len(test_riv_1), \
        ("RIV.__len__() has failed. These two should be equal:\n"
         "{} != {}").format(test_size, len(test_riv_1))

    test_riv_2 = make_test_riv(2)
    assert test_riv_1 == test_riv_1, \
        "RIV.__eq__() has failed. test_riv_1 should be == to itself."
    assert not test_riv_1 == test_riv_2, \
        "RIV.__eq__() has failed. test_riv_1 should not be == to test_riv_2"

    assert test_riv_2 == test_riv_1 * 2, \
        ("RIV.__mult__() has failed. These two should be equal:"
         "{} != {}").format(test_riv_2, test_riv_1 * 2)

    assert test_key_a in test_riv_1, \
        ("RIV.__contains__() has failed.\n"
         "{} should be in {}").format(test_key_a, test_riv_1)

    assert bad_key not in test_riv_1, \
        ("RIV.__contains__() has failed.\n"
         "{} should not be in {}").format(bad_key, test_riv_1)

    assert test_val_a == test_riv_1[test_key_a], \
        ("RIV.__getitem__() has failed.\n"
         "{}[{}]['value]' should be {}").format(test_riv_1, test_key_a, test_val_a)
    assert 0 == test_riv_1[bad_key], \
        ("RIV.__getitem__() has failed.\n"
         "{}[{}]['value]' should be 0").format(test_riv_1, bad_key)

    assert test_riv_1 + test_riv_1 == test_riv_1 * 2, \
        ("RIV.__add__() has failed.\n"
         "{} + itself should be equal to {}").format(test_riv_1, test_riv_1 * 2)

    assert test_riv_1 * -1 == -test_riv_1, \
        ("RIV.__neg__() has failed.\n"
         "{} negated should be equal to {}").format(test_riv_1, test_riv_1 * -1)

    assert test_riv_1 * 0 == test_riv_1 - test_riv_1, \
        ("RIV.__sub__() has failed.\n"
         "{} minus itself should be equal to {}").format(test_riv_1, test_riv_1 * 0)

    assert test_riv_1 * 0.5 == test_riv_1 / 2, \
        ("RIV.__truediv__() has failed.\n"
         "{} / 2 should be equal to {}").format(test_riv_1, test_riv_1 * 0.5)

    assert test_is == test_riv_1.keys(), \
        ("RIV.keys() has failed.\n"
         "{}.keys() should be equal to {}").format(test_riv_1, test_is)

    assert test_vs == test_riv_1.vals(), \
        ("RIV.vals() has failed.\n"
         "{}.vals() should be equal to {}").format(test_riv_1, test_vs)

    test_riv_zeros = RIV.from_sets(100, (4, 6, 0), (1, 0, -1))
    assert test_riv_1 == test_riv_zeros.remove_zeros(), \
        ("RIV.remove_zeros has failed.\n"
         "{}.remove_zeros() should be equal to {}").format(test_riv_zeros, test_riv_1)

    mag = sum(i ** 2 for i in test_vs) ** 0.5
    assert mag == test_riv_1.magnitude(), \
        ("RIV.magnitude() has failed.\n"
         "{}.magnitude() should be equal to {}").format(test_riv_1, mag)

    assert 1 == round(test_riv_1.normalize().magnitude(), 0), \
        ("RIV.normalize() has failed.\n"
         "{}.normalize() should have magnitude 1").format(test_riv_1)
    test_riv_plus = test_riv_1.permute(test_perms, test_permutation_factor)
    test_riv_minus = test_riv_1.permute(test_perms, -test_permutation_factor)
    assert test_riv_1 != test_riv_plus, \
        ("RIV.permute() has failed.\n"
         "A positive permutation of a riv should not be equal to the riv itself.\n"
         "{} == {}\n"
         "Try with different values or find a new random.").format(test_riv_1, test_riv_plus)
    assert test_riv_1 != test_riv_minus, \
        ("RIV.permute() has failed.\n"
         "A negative permutation of a riv should not be equal to the riv itself.\n"
         "{} == {}\n"
         "Try with different values or find a new random.").format(test_riv_1, test_riv_minus)
    assert test_riv_plus != test_riv_minus, \
        ("RIV.permute() has failed.\n"
         "A negative permutation should not be equal to the positive permuation of the same riv.\n"
         "{} == {}\n"
         "Try with different values or find a new random.").format(test_riv_plus, test_riv_minus)
    assert test_riv_1 == test_riv_plus.permute(test_perms, -test_permutation_factor), \
        ("RIV.permute() has failed.\n"
         "A positive permutation should reverse to the original riv.\n"
         "{} != {}\n"
         "Try with different values or find a new random.").format(test_riv_1,
                                                                   test_riv_plus.permute(test_perms,
                                                                                         -test_permutation_factor))
    assert test_riv_1 == test_riv_minus.permute(test_perms, test_permutation_factor), \
        ("RIV.permute() has failed.\n"
         "A negative permutation should reverse to the original riv.\n"
         "{} != {}\n"
         "Try with different values or find a new random.").format(test_riv_1,
                                                                   test_riv_plus.permute(test_perms,
                                                                                         test_permutation_factor))
    test_nnz = test_size // 10
    test_riv_gen_1 = riv.generate_riv(test_size, test_nnz, "token1")
    test_riv_gen_2 = riv.generate_riv(test_size, test_nnz, "token2")
    assert test_riv_gen_1 == riv.generate_riv(test_size, test_nnz, "token1"), \
        ("riv.generate_riv() has failed.\n"
         "Given identical inputs, it should produce the same results every time."
         "{} should be equal to {}.").format(test_riv_gen_1, riv.generate_riv(test_size, test_nnz, "token1"))
    assert test_riv_gen_2 == riv.generate_riv(test_size, test_nnz, "token2"), \
        ("riv.generate_riv() has failed.\n"
         "Given identical inputs, it should produce the same results every time."
         "{} should be equal to {}.").format(test_riv_gen_2, riv.generate_riv(test_size, test_nnz, "token2"))
    assert test_riv_gen_1 != test_riv_gen_2, \
        ("riv.generate_riv() has failed.\n"
         "Two different tokens should produce different rivs."
         "{} should not be equal to {}.").format(test_riv_gen_1, test_riv_gen_2)