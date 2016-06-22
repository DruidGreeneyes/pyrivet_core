import functools
import re
from .dict_riv import generate_riv
from .dict_riv import RIV
from .vec_perms import Permutations as Perms
from .util import cached_function
import random


def _break_text(text, pattern):
    return pattern.split(text)


def _cycle_context(length, nums, position):
    return nums[position + 1:length] + nums[:position]


def _merge_update(destination, update):
    for k in update:
        if k in destination:
            destination[k] += update[k]
        else:
            destination[k] = update[k]


class Lexicon(dict):

    def __init__(self, size, nnz):
        super(Lexicon, self).__init__()
        self._size = size
        rand = random.Random()
        self._generate = functools.partial(generate_riv, int(size), int(nnz), rand=rand)
        self._perms = Perms.generate(size)

    def __missing__(self, word):
        ind = self._generate(word)
        self[word] = [ind, ind]
        return self[word]

    def count(self):
        return len(self)

    def size(self):
        return self._size

    def get_lex(self, word):
        return self[word][0]

    def get_ind(self, word):
        return self[word][1]

    @cached_function
    def get_mean_vector(self):
        rivs = self.values()
        rivs = [e[0] for e in rivs]
        total_riv = RIV.sum(*rivs, size=self._size)
        count = self.count()
        return total_riv / count

    def cache(self, words):
        for word in words:
            self[word]

    def _add_to_lex(self, word, riv):
        self[word][0] += riv

    def _update(self, updates):
        self.get_mean_vector.invalidate()
        for k in updates:
            self._add_to_lex(k, updates[k])

    def _process_sentence(self, word_pattern, sentence):
        def processor(index):
            words = sentence[:index] + sentence[index + 1:]
            rivs = map(self.get_lex, words)
            return RIV.sum(*rivs, size=self._size)

        words = tuple(word_pattern.split(sentence))
        indices = range(len(words))
        rivs = map(processor, indices)
        return dict(zip(words, rivs))

    def ingest_text(self, text, sentence_pattern=re.compile(r"\.\s+"), word_pattern=re.compile(r"\s+")):
        updates = dict()
        sentences = sentence_pattern.split(text)
        sentences = filter(lambda s: len(s) > 1, sentences)
        processor = functools.partial(self._process_sentence, word_pattern)
        sentence_updates = map(processor, sentences)
        for word_update in sentence_updates:
            _merge_update(updates, word_update)
        self.update(updates)

    def _process_broken_sentence(self, broken_sentence):
        def processor(index):
            words = broken_sentence[:index] + broken_sentence[index + 1:]
            rivs = tuple(map(self.get_ind, words))
            return RIV.sum(*rivs, size=self._size)

        indices = tuple(range(len(broken_sentence)))
        rivs = tuple(map(processor, indices))
        return dict(zip(broken_sentence, rivs))

    def ingest_broken_text(self, broken_text):
        updates = dict()
        sentence_updates = tuple(map(self._process_broken_sentence, broken_text))
        for word_update in sentence_updates:
            _merge_update(updates, word_update)
        self._update(updates)
