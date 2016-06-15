from unittest import TestCase

from riv.vector_element import VectorElement as V
import pytest


class T(TestCase):

    def test_make(self):
        assert "4|1.0" == str(V.make(4, 1))

    def test__eq(self):
        assert V.make(4, 1) == V.make(4, 1)
        assert V.make(4, 3) == V.make(4, 1)
        assert V.make(4, 1) != V.make(6, 1)

    def test_partial(self):
        assert V.make(4, 1) == V.partial(4)
        assert V.make(4, 1) != V.partial(1.0)
        assert V.make(0, 1) == V.partial(1.0)

    def test_from_str(self):
        assert V.make(4, 1) == V.from_str("4|1")

    def test__get_item(self):
        v_elt = V.make(4, 1)
        assert 4 == v_elt['index'], v_elt[0]
        assert 1 == v_elt['value'], v_elt[1]
        with pytest.raises(IndexError): v_elt['blarg']

    def test__str(self):
        assert "4|1.0" == str(V.make(4, 1))

    def test__add(self):
        v_elt = V.make(4, 1)
        assert V.make(4, 2) == v_elt + 1
        assert V.make(4, 2) == v_elt + v_elt
        with pytest.raises(IndexError):
            v_elt + V.make(6, 2)

    def test__sub(self):
        v_elt = V.make(4, 1)
        assert V.make(4, 0) == v_elt - 1
        assert V.make(4, 0) == v_elt - v_elt
        with pytest.raises(IndexError):
            v_elt - V.make(6, 2)

    def test__mult(self):
        v_elt = V.make(4, 2)
        assert V.make(4, 0) == v_elt * 0

    def test__truediv(self):
        v_elt = V.make(4, 2)
        assert V.make(4, 1) == v_elt / 2

    def test__neg(self):
        v_elt = V.make(4, 1)
        assert V.make(4, -1) == -v_elt

    def test__contains(self):
        v_elt = V.make(4, 1)
        assert 1 in v_elt
        assert not (4 in v_elt)

    def test_strict_equals(self):
        v_elt = V.make(4, 1)
        assert v_elt.strict_equals(v_elt)
        assert not v_elt.strict_equals(V.make(4, 2))

    def test_not_zero(self):
        assert V.make(4, 1).not_zero()
        assert not V.make(4, 0.0000001).not_zero()
