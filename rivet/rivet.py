from riv.dict_riv import generate_riv
from riv.dict_riv import RIV
import re
import functools
import itertools
import random
from datetime import datetime


DEF_SENTENCE_PATTERN = re.compile(r"\.\s+")
DEF_WORD_PATTERN = re.compile(r"\s+")


def similarity(riva, rivb):
    mag = riva.magnitude() * rivb.magnitude()
    if mag:
        d = RIV.dot_product(riva, rivb)
        return round(d / mag, 6)
    else:
        return 0


def bulk_similarity(rivs):
    id_rivs = dict(zip(range(len(rivs)), rivs))

    def id_sim(id_a, id_b):
        sim = similarity(id_rivs[id_a], id_rivs[id_b])
        return (id_a, id_b), sim

    def aggregate_sim(identity, id):
        similarities, ids = identity
        simmer = functools.partial(id_sim, id)
        sims = map(simmer, ids)
        for sim in sims:
            similarities.append(sim)
        ids.append(id)
        return similarities, ids
    keys = tuple(id_rivs.keys())
    res = ([], [])
    for key in keys:
        res = aggregate_sim(res, key)
    return res[0]


def compare_words(lexicon, worda, wordb):
    mv = lexicon.get_mean_vector()
    return similarity(lexicon.get_lex(worda) - mv, lexicon.get_lex(wordb) - mv)


def _aggregate_words(sentence_pattern, word_pattern, *texts, distinct=True):
    def word_splitter(sentences):
        broken_sentences = map(word_pattern.split, sentences)
        return tuple(broken_sentences)

    def chain(broken_sentences):
        return itertools.chain(*broken_sentences)
    sentence_texts = map(sentence_pattern.split, texts)
    broken_texts = map(word_splitter, sentence_texts)
    broken_texts = tuple(broken_texts)
    joined_sentences = map(chain, broken_texts)
    joined_words = itertools.chain(*joined_sentences)
    words = set(joined_words) if distinct else tuple(joined_words)
    words = words
    return words, broken_texts


def deep_process_text(lexicon, text, sentence_pattern=DEF_SENTENCE_PATTERN, word_pattern=DEF_WORD_PATTERN):
    mv = lexicon.get_mean_vector()
    words = _aggregate_words(sentence_pattern, word_pattern, text, distinct=False)
    rivs = map(lexicon.get_lex, words)
    riv = RIV.sum(*rivs, size=lexicon._size)
    return riv - mv


def deep_process_broken(lexicon, broken_text, mv=None):
    num_sentences = len(broken_text)
    sentence_lengths = map(len, broken_text)
    num_words = sum(sentence_lengths)
    print("Processing test: {} sentences, {} words.".format(num_sentences, num_words))
    if mv is None:
        mv = lexicon.get_mean_vector()
    words = list(itertools.chain(*broken_text))
    rivs = map(lexicon.get_lex, words)
    riv = RIV.sum(*rivs, size=lexicon._size)
    return riv - mv


def process_text(text, size=1000, nnz=8, sentence_pattern=DEF_SENTENCE_PATTERN, word_pattern=DEF_WORD_PATTERN):
    rand = random.Random()
    generator = functools.partial(generate_riv, size, nnz, rand=rand)
    words = _aggregate_words(sentence_pattern, word_pattern, text, distinct=False)
    rivs = map(generator, words)
    return RIV.sum(*rivs, size=size)


def bulk_process(texts, sentence_pattern, word_pattern, size=100, nnz=4):
    rand = random.Random()
    generate = functools.partial(generate_riv, size, nnz, rand=rand)

    def generate_map_entry(word):
        riv = generate(word)
        return word, riv
    word_map, broken_texts = _aggregate_words(sentence_pattern, word_pattern, *texts)
    word_map = dict(map(generate_map_entry, word_map))

    def process(broken_text):
        words = list(itertools.chain(*broken_text))
        rivs = map(word_map.get, words)
        return RIV.sum(*rivs, size=size)

    rivs = map(process, broken_texts)
    return tuple(rivs)


def _compare_documents(texta, textb, lexicon=None, ingest=False):
    if lexicon is not None:
        if ingest:
            lexicon.ingest(texta)
            lexicon.ingest(textb)
        riva = deep_process_text(lexicon, texta)
        rivb = deep_process_text(lexicon, textb)
        return similarity(riva, rivb)
    else:
        riva = process_text(texta)
        rivb = process_text(textb)
        return similarity(riva, rivb)


def _lex_compare_docs(lexicon, texts, ingest, sentence_pattern=DEF_SENTENCE_PATTERN, word_pattern=DEF_WORD_PATTERN):
    words, broken_texts = _aggregate_words(sentence_pattern, word_pattern, *texts)
    lexicon.cache(words)
    if ingest:
        for text in broken_texts:
            lexicon.ingest_broken_text(text)
    mean_vector = lexicon.get_mean_vector()
    processor = functools.partial(deep_process_broken, lexicon, mv=mean_vector)
    rivs = []
    for text in broken_texts:
        riv = processor(text)
        rivs.append(riv)
    rivs = tuple(rivs)
    print("Comparing {} document rivs.".format(len(rivs)))
    sims = bulk_similarity(rivs)
    print("similarities: {}".format(sims))
    return sims


def compare_documents(*texts, lexicon=None, ingest=False, sentence_pattern=DEF_SENTENCE_PATTERN, word_pattern=DEF_WORD_PATTERN):
    if lexicon is not None:
        sims = _lex_compare_docs(lexicon, texts, ingest, sentence_pattern, word_pattern)
        return sims
    else:
        rivs = bulk_process(texts, sentence_pattern, word_pattern)
        sims = bulk_similarity(rivs)
        return sims
