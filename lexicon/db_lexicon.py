import functools
import re
from riv.dict_riv import generate_riv
from riv.dict_riv import RIV
from riv.vec_perms import Permutations as Perms
from db.serializers import RIVSerializer, PermutationSerializer
from tinydb_serialization import SerializationMiddleware
from tinydb import TinyDB, where
from tinyrecord import transaction
import random


serialization = SerializationMiddleware()
serialization.register_serializer(RIVSerializer(), 'RIVSerializer')
serialization.register_serializer(PermutationSerializer(), 'PermutationSerializer')


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


def _meta_table_get(table, slot):
    return table.get(where('slot') == slot)['value']


def _lex_table_get(table, word):
    return table.get(where('word') == word)['riv']


class Lexicon(object):

    def __init__(self, db):
        self._db = db
        self._lex = db.table('lexicon')
        self._meta = db.table('metadata')
        self._name = self.get_meta('name')
        self._size = self.get_meta('size')
        self._nnz = self.get_meta('nnz')
        self._perms = self.get_meta('permutations')
        self._updates = {}
        self._up_to_date = False
        self._mean_vector = None
        self._count = None

        rand = random.Random()
        self.get_ind = functools.partial(generate_riv, self._size, self._nnz, rand=rand)
        self._get_word = functools.partial(_lex_table_get, self._lex)
        self.get_meta = functools.partial(_meta_table_get, self._meta)

    def __enter__(self):
        pass

    def __exit__(self):
        if self._updates:
            self._update_words(self._updates)
        self._db.close()

    def __contains__(self, word):
        return self._get_word(word) is not None

    def _get_words(self, *words):
        return self._lex.search(where('word').test(lambda w: w in words))

    def count(self):
        if self._up_to_date:
            return self._count
        else:
            self.get_mean_vector()
            return self._count

    def size(self):
        return self._size

    def get_lex(self, word):
        riv = self._get_word(word)
        return riv if riv else self.get_ind(word)

    def get_mean_vector(self):
        if self._up_to_date:
            return self._mean_vector
        else:
            rivs = self._lex.all()
            rivs = tuple(map(lambda d: d['riv'], rivs))
            total_riv = RIV.sum_rivs(*rivs, size=self._size)
            self._count = len(self._lex)
            self._mean_vector = total_riv / self._count
            self._up_to_date = True
            return self._mean_vector

    def _update_words(self, updates):
        self._up_to_date = False
        words = tuple(updates.keys())
        new_words = []
        known_words = []
        for word in words:
            if word in self:
                known_words += word
            else:
                new_words += word
        with transaction(self._lex) as tr:
            for word in known_words:
                tr.update({'riv': updates[word]}, where('word') == word)
            for word in new_words:
                tr.insert({'word': word, 'riv': updates[word]})

    def _add_lex(self, word, riv):
        if word in self._updates:
            self._updates[word].destructive_add(riv)
        else:
            self._updates[word] = riv
        if len(self._updates) > self.count() / 10:
            self._update_words(self._updates)

    def update(self, updates):
        for k in updates:
            self._add_lex(k, updates[k])

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

    @staticmethod
    def new_lexicon(size, nnz, name, db_path=None):
        db_path = db_path if db_path else "dbs/{}.json".format(name)
        db = TinyDB(db_path)
        meta = db.table('metadata')
        lex = db.table('lexicon')
        if len(lex):
            raise LookupError("{} appears to be an existing lexicon; "
                              "either delete it or try again with a "
                              "new name.".format(name))
        else:
            db.purge()
            perms = Perms.generate(size)
            meta.insert({'slot': 'size', 'value': size})
            meta.insert({'slot': 'nnz', 'value': nnz})
            meta.insert({'slot': 'name', 'value': name})
            meta.insert({'slot': 'permutations', 'value': perms})
            return Lexicon(db)

