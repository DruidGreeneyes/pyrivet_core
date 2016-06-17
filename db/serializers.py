from riv.dict_riv import RIV
from riv.vec_perms import Permutations as Perms
from tinydb_serialization import Serializer


class RIVSerializer(Serializer):
    OBJ_CLASS = RIV

    encode = RIV.to_str

    decode = RIV.from_str


class PermutationSerializer(Serializer):
    OBJ_CLASS = Perms

    encode = Perms.to_str

    decode = Perms.from_str