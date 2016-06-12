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
        
    def __cmp_index__(self, v_elt):
        return self['index'] - v_elt['index']
    
    def __cmp_value__(self, v_elt):
        return self['index'] - v_elt['index']
    
    def __lt__(self, v_elt): return self['index'] < v_elt['index']

    def __le__(self, v_elt): return self['index'] <= v_elt['index']

    def __eq__(self, v_elt): return self['index'] == v_elt['index']

    def __ne__(self, v_elt): return self['index'] != v_elt['index']

    def __gt__(self, v_elt): return self['index'] > v_elt['index']

    def __ge__(self, v_elt): return self['index'] >= v_elt['index']

    def __str__(self):
        return "{}|{}".format(self['index'], self['value'])
    
    def __repr__(self):
        return str(self)
    
    @dispatch(float)
    def __add__(self, value):
        return VectorElement.make(self['index'], value + self['value'])
    
    @dispatch(object)
    def __add__(self, v_elt):
        if VectorElement.index_equals(self, v_elt):
            return self + v_elt['value']
        else:
            raise IndexError("Cannot add elements whose indices don't match:\n"
                             "{} + {}".format(self, v_elt))
                
    @dispatch(float)
    def __sub__(self, value):
        return self + (-value)
    
    @dispatch(object)
    def __sub__(self, v_elt):
        return self + -v_elt
    
    def __mul__(self, scalar):
        return VectorElement.make(self['index'], scalar * self['value'])
    
    def __truediv__(self, scalar):
        return VectorElement.make(self['index'], self['value'] / scalar)
    
    def __neg__(self):
        return VectorElement.make(self['index'], -self['value'])
    
    def __int__(self): self.__index__()

    def __index__(self): return self['index']
    
    def strict_equals(self, v_elt):
        return self['index'] == v_elt['index'] and self['value'] == v_elt['value']
    
    def contains(self, value): return value == self['value']

    def not_zero(self):
        return round(self['value'], 6) != 0

    @staticmethod
    def make(index, value): return VectorElement(index, value)

    @staticmethod
    def from_index(index): return VectorElement.make(index, 0.0)

    @staticmethod
    def from_value(value): return VectorElement.make(0, float(value))

    @staticmethod
    def zero_elt(): return VectorElement.make(0, 0.0)

    @staticmethod
    def from_str(string):
        bits = string.split("|")
        return VectorElement.make(int(bits[0]), float(bits[1]))

    @staticmethod
    def compare(v_elt1, v_elt2): return v_elt1.__cmp_index__(v_elt2)

    @staticmethod
    def contains(v_elt, value): return value == v_elt['value']

    @staticmethod
    def index_equals(v_elt, index): return index == v_elt['index']

    @staticmethod
    def strict_equals(v_elt1, v_elt2): return v_elt1.strict_equals(v_elt2)



