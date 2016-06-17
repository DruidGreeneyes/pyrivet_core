import functools
import re
from riv.dict_riv import generate_riv
from riv.dict_riv import RIV
from riv.vec_perms import Permutations as Perms
import random


def _break_text(text, pattern):
    return pattern.split(text)


def _cycle_context(length, nums, position):
    return nums[position + 1:length] + nums[:position]


def _merge_update(destination, update):
    for k in update:
        if k in destination:
            destination[k].destructive_add(update[k])
        else:
            destination[k] = update[k]


class Lexicon(object):

    def __init__(self, size, nnz):
        self._lexicon = dict()
        self._size = size
        rand = random.Random()
        self.get_ind = functools.partial(generate_riv, int(size), int(nnz), rand=rand)
        self._perms = Perms.generate(size)
        self._up_to_date = False
        self._mean_vector = None

    def count(self):
        return len(self._lexicon)

    def size(self):
        return self._size

    def get_lex(self, word):
        return self._lexicon.get(word, self.get_ind(word))

    def get_mean_vector(self):
        if self._up_to_date:
            return self._mean_vector
        else:
            rivs = self._lexicon.values()
            total_riv = RIV.sum_rivs(*rivs, size=self._size)
            self._mean_vector = total_riv / len(self._lexicon)
            self._up_to_date = True
            return self._mean_vector

    def update_lex(self, word, riv):
        self._up_to_date = False
        self._lexicon[word] = riv

    def add_lex(self, word, riv):
        if word in self._lexicon:
            self._lexicon[word].destructive_add(riv)
        else:
            self._lexicon[word] = riv

    def update(self, updates):
        for k in updates:
            self.add_lex(k, updates[k])

    def _process_context(self, words, context):
        w = map(words.__getitem__, context)
        inds = map(self.get_ind, w)
        return RIV.sum_rivs(*inds, size=self._size)

    def _process_sentence(self, word_pattern, sentence):
        words = tuple(word_pattern.split(sentence))
        num_words = len(words)
        positions = tuple(range(num_words))
        cycler = functools.partial(_cycle_context, num_words, positions)
        contexts = map(cycler, positions)
        processor = functools.partial(self._process_context, words)
        rivs = map(processor, contexts)
        return dict(zip(words, rivs))

    def ingest(self, text, sentence_pattern=re.compile(r"\.\s+"), word_pattern=re.compile(r"\s+")):
        updates = dict()
        sentences = sentence_pattern.split(text)
        sentences = filter(lambda s: len(s) > 1, sentences)
        processor = functools.partial(self._process_sentence, word_pattern)
        sentence_updates = map(processor, sentences)
        for word_update in sentence_updates:
            _merge_update(updates, word_update)
        self.update(updates)
