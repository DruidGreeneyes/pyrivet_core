from lexicon.lexicon import Lexicon
from riv.dict_riv import generate_riv
from riv.dict_riv import RIV
import re
import functools as FT
import random


def _dot_product(riva, rivb):
    return sum(riva[i] * rivb[i] for i in riva.keys() if i in riva and i in rivb)


def similarity(riva, rivb):
    mag = riva.magnitude() * rivb.magnitude()
    return 0 if mag == 0 else round(_dot_product(riva, rivb) / mag, 6)


def compare_words(lexicon, worda, wordb):
    mv = lexicon.get_mean_vector()
    return similarity(lexicon.get_lex(worda) - mv, lexicon.get_lex(wordb) - mv)


def deep_process_text(lexicon, text, split_pattern=re.compile(r"\.?\s+")):
    mv = lexicon.get_mean_vector()
    words = split_pattern.split(text)
    rivs = map(lexicon.get_lex, words)
    riv = RIV.sum_rivs(*rivs, size=lexicon._size)
    return riv - mv


def process_text(text, split_pattern=re.compile(r"\.?\s+"), size=1000, nnz=8):
    rand = random.Random()
    generator = FT.partial(generate_riv, size, nnz, rand=rand)
    words = split_pattern.split(text)
    rivs = map(generator, words)
    return RIV.sum_rivs(*rivs, size=size)


def compare_documents(texta, textb, lexicon=None, ingest=False):
    if ingest and isinstance(lexicon, Lexicon):
        lexicon.ingest(texta)
        lexicon.ingest(textb)
        return similarity(deep_process_text(lexicon, texta),
                          deep_process_text(lexicon, textb))
    else:
        return similarity(process_text(texta),
                          process_text(textb))
