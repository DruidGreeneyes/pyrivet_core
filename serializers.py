from .dict_riv import RIV
from .vec_perms import Permutations as Perms
from tinydb_serialization import Serializer


class RIVSerializer(Serializer):
    OBJ_CLASS = RIV

    def encode(self, obj):
        return RIV.to_str(obj)

    def decode(self, string):
        return RIV.from_str(string)


class PermutationSerializer(Serializer):
    OBJ_CLASS = Perms

    def encode(self, obj):
        return Perms.to_str(obj)

    def decode(self, string):
        return Perms.from_str(string)
