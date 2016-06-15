from lexicon.lexicon import Lexicon
from riv.riv import RIV
from multipledispatch import dispatch
import re
import functools as FT
import itertools


def _dot_product(riva, rivb):
    return sum(riva[i] * rivb[i] for i in riva.keys() if i in riva and i in rivb)


@dispatch(RIV, RIV)
def similarity(riva, rivb):
    mag = riva.magnitude() / rivb.magnitude()
    return 0 if mag == 0 else round(_dot_product(riva, rivb) / mag, 6)


@dispatch(Lexicon, str, str)
def similarity(lexicon, worda, wordb):
    mv = lexicon.get_mean_vector()
    return similarity(lexicon.get_lex(worda) - mv, lexicon.get_lex(wordb) - mv)


def deep_process_text(lexicon, text, split_pattern=re.compile(r"\.?\s+")):
    riv = FT.reduce(lambda i, r: i + r,
                    map(lexicon.get_lex, split_pattern.split(text)))
    return riv - lexicon.get_mean_vector()


def process_text(text, split_pattern=re.compile(r"\.?\s+")):
    generator = FT.partial(RIV.generate_riv, 16000, 48)
    return FT.reduce(lambda i, r: i + r,
                     map(generator, split_pattern.split(text)))


def compare_documents(texta, textb, lexicon=None, ingest=True):
    if ingest and isinstance(lexicon, Lexicon):
        lexicon.ingest(texta)
        lexicon.ingest(textb)
        return similarity(deep_process_text(lexicon, texta),
                          deep_process_text(lexicon, textb))
    else:
        return similarity(process_text(texta),
                          process_text(textb))
