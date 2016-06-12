'''
Created on 7 May 2016

@author: josh
'''

# vector_element is an immutable int/float pair used to represent
# a value mapped to an index in a compressed sparse vector.

from multipledispatch import dispatch


class VectorElement(object):
    __slots__ = ['_point']
    
    def __init__(self, index, value):
        self._point = (int(index), float(value))
        
    def __getitem__(self, part):
        if part == 'index' or part == 0: return self._point[0]
        elif part == 'value' or part == 1: return self._point[1]
        else:
            raise IndexError("VectorElement only contains "
                             "entries for 'index'(0) and 'value'(1).\n"
                             "You have asked for: {}".format(part))

    @dispatch(int)
    def __lt__(self, index):
        return self['index'] < index

    @dispatch(object)
    def __lt__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric <"):
            return self < v_elt['index']

    @dispatch(int)
    def __le__(self, index):
        return self['index'] <= index

    @dispatch(object)
    def __le__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric <="):
            return self <= v_elt['index']

    @dispatch(int)
    def __eq__(self, index): return self['index'] == index

    @dispatch(object)
    def __eq__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric =="):
            return self == v_elt['index']

    @dispatch(int)
    def __ne__(self, index): return self['index'] != index

    @dispatch(object)
    def __ne__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric !="):
            return self != v_elt['index']

    @dispatch(int)
    def __gt__(self, index):
        return self['index'] > index

    @dispatch(object)
    def __gt__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric >"):
            return self > v_elt['index']

    @dispatch(int)
    def __ge__(self, index):
        return self['index'] >= index

    @dispatch(object)
    def __ge__(self, v_elt):
        if VectorElement._validate_type(v_elt, "numeric >="):
            return self >= v_elt['index']

    def __str__(self):
        return "{}|{}".format(self['index'], self['value'])
    
    def __repr__(self):
        return str(self)

    @dispatch(float)
    def __add__(self, value):
        return VectorElement.make(self['index'], value + self['value'])

    @dispatch(int)
    def __add__(self, value):
        return self + float(value)

    @dispatch(object)
    def __add__(self, v_elt):
        if self._validate_index(v_elt, "addition"):
            return self + v_elt['value']

    @dispatch(float)
    def __sub__(self, value):
        return self + (-value)

    @dispatch(int)
    def __sub__(self, value):
        return self + (-value)

    @dispatch(object)
    def __sub__(self, v_elt):
        if (VectorElement._validate_type(v_elt, "subtraction") and
                self._validate_index(v_elt, "subtraction")):
            return self - v_elt['value']

    def __mul__(self, scalar):
        return VectorElement.make(self['index'], scalar * self['value'])
    
    def __truediv__(self, scalar):
        return VectorElement.make(self['index'], self['value'] / scalar)
    
    def __neg__(self):
        return VectorElement.make(self['index'], -self['value'])
    
    def __int__(self): return self['index']

    def __index__(self): return int(self)

    def __hash__(self): return int(self)

    def __contains__(self, value):
        return round(self['value'] - value, 6) == 0

    def strict_equals(self, v_elt):
        return self['index'] == v_elt['index'] and self['value'] == v_elt['value']

    def not_zero(self):
        return round(self['value'], 6) != 0

    def _validate_index(self, v_elt, op_name):
        if self == v_elt:
            return True
        else:
            raise IndexError(
                ("Cannot perform {} on elements whose indices don't match:\n"
                 "{} - {} = OMGWTFBBQLAWRENCE.").format(op_name, self, v_elt))

    @staticmethod
    def make(index, value): return VectorElement(index, value)

    @staticmethod
    @dispatch(int)
    def partial(index): return VectorElement.make(index, 0.0)

    @staticmethod
    @dispatch(float)
    def partial(value): return VectorElement.make(0, float(value))

    @staticmethod
    def zero_elt(): return VectorElement.make(0, 0)

    @staticmethod
    def from_str(string):
        bits = string.split("|")
        return VectorElement.make(int(bits[0]), float(bits[1]))

    @staticmethod
    def _validate_type(obj, op_name):
        if isinstance(obj, VectorElement):
            return True
        else:
            raise TypeError("VectorElement cannot perform {} against {}.".format(op_name, type(obj)))
