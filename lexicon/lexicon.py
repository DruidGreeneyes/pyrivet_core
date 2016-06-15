import functools
import re
from riv.riv import RIV as RIV
from riv.vec_perms import Permutations as Perms


class Lexicon(object):

    def __init__(self, size, nnz):
        self._lexicon = dict()
        self.get_ind = functools.partial(RIV.generate_riv, int(size), int(nnz))
        self._perms = Perms.generate(size)

    def count(self):
        return len(self._lexicon)

    def get_lex(self, word):
        return self._lexicon.get(word, self.get_ind(word))

    def get_mean_vector(self):
        return sum(self._lexicon.values()) / self.count()

    def update_lex(self, word, riv):
        self._lexicon[word] = riv

    def add_lex(self, word, riv):
        self.update_lex(word, self.get_lex(word) + riv)

    def update(self, updates):
        for k in updates:
            self.add_lex(k, updates[k])

    def _break_text(self, text, pattern=re.compile(r"\.\s+")):
        return pattern.split(text)

    def _cycle_context(self, length, nums, position):
        return nums[position:length] + nums[:position]

    def _process_context(self, words, context):
        return functools.reduce(lambda i, r: i + r,
                                map(self.get_ind,
                                    map(lambda i: words[i],
                                        context[1:])))

    def _process_sentence(self, sentence_pattern, sentence):
        words = tuple(sentence_pattern.split(sentence))
        num_words = len(words)
        positions = tuple(range(num_words))
        contexts = map(functools.partial(self._cycle_context, num_words, positions),
                       positions)
        rivs = map(functools.partial(self._process_context, words),
                   contexts)
        return dict(zip(words, rivs))

    def _merge_update(self, updates, update):
        for k in update:
            updates[k] = (update[k] if k not in updates else updates[k] + update[k])

    def ingest(self, text, sentence_pattern=re.compile(r"\.\s+"), word_pattern=re.compile(r"\s+")):
        updates = dict()
        map(functools.partial(self._merge_update, updates),
            map(functools.partial(self._process_sentence, word_pattern),
                sentence_pattern.split(text)))
        self.update(updates)
