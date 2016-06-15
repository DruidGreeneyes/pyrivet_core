from multipledispatch import dispatch


def immutable_pair(left_name='left', right_name='right'):
    def wrapper(Cls):
        class PairClass(object):
            __slots__ = ['_parts']

            @dispatch(object, object)
            def __init__(self, left, right):
                self._parts = (left, right)

            def __getitem__(self, part):
                if part == left_name or part == 0:
                    return self._parts[0]
                elif part == right_name or part == 1:
                    return self._parts[1]
                else:
                    raise IndexError("{} only contains "
                                     "entries for {}(0) and {}(1).\n"
                                     "You have asked for: {}".format(str(Cls), left_name, right_name, part))

            def __str__(self):
                return "|".join(map(str, self._parts))

            def __repr__(self):
                return str(self)

            def __getattribute__(self, s):
                try:
                    x = super(PairClass, self).__getattribute__(s)
                except AttributeError:
                    pass
                else:
                    return x
                return self.oInstance.__getattribute__(s)
        return PairClass
    return wrapper