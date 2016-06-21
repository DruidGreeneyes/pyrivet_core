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
serialization.register_serializer(RIVSerializer(), 'RIV')
serialization.register_serializer(PermutationSerializer(), 'Permutations')


def _cycle_context(length, nums, position):
    return nums[position + 1:length] + nums[:position]


def _merge_update(destination, update):
    for k in update:
        if k in destination:
            destination[k].destructive_add(update[k])
        else:
            destination[k] = update[k]


def _open_db(db_path):
    return TinyDB(db_path, storage=serialization)


def _meta_table_get(table, slot):
    entry = table.get(where('slot') == slot)
    return entry['value'] if entry else None


def _lex_table_get(table, word):
    return table.get(where('word') == word)


class lexicon(object):

    def __init__(self, db):
        self._db = db
        self._lex = db.table('lexicon')
        self._meta = db.table('metadata')

        self.get_meta = functools.partial(_meta_table_get, self._meta)
        self._name = self.get_meta('name')
        self._size = self.get_meta('size')
        self._nnz = self.get_meta('nnz')
        self._perms = self.get_meta('permutations')

        self._updates = {}
        self._up_to_date = False
        self._mean_vector = None
        self._count = None
        self._cache = {}

        rand = random.Random()
        self._generate = functools.partial(generate_riv, self._size, self._nnz, rand=rand)
        self._db_get = functools.partial(_lex_table_get, self._lex)

    def __enter__(self):
        return self

    def purge(self):
        self._db.purge()
        self._updates.clear()

    def close(self):
        if self._updates:
            self._update_words(self._updates)
        self._db.close()

    def __exit__(self, type, value, traceback):
        self.close()

    def _get_word(self, word):
        res = self._cache.get(word, None)
        return res if res else self._db_get(word)

    def _db_get_words(self, words):
        return self._lex.search(where('word').any(words))

    def _db_all_filter(self, words):
        all = self._lex.all()
        res = filter(lambda e: e['word'] in words, all)
        return tuple(res)

    def __contains__(self, word):
        entry = self._get_word(word)
        res = entry.get('known', False)
        res = res
        return res

    def get_ind(self, word):
        res = self._get_word(word)
        if res and 'ind' in res:
            return res['ind']
        else:
            return self._generate(word)

    def get_lex(self, word):
        res = self._get_word(word)
        if res:
            return res['lex']
        else:
            return self._generate(word)

    def get_mean_vector(self):
        if self._up_to_date:
            return self._mean_vector
        else:
            rivs = self._lex.all()
            rivs = tuple(map(lambda d: d['lex'], rivs))
            total_riv = RIV.sum(*rivs, size=self._size)
            self._count = len(self._lex)
            self._mean_vector = total_riv / self._count
            self._up_to_date = True
            return self._mean_vector

    def cache(self, words):
        print("caching {} unique words...".format(len(words)))
        self._cache.clear()
        known_words = self._db_get_words(words)
#        known_words = self._db_all_filter(words)
#        known_words = map(self._db_get, words)
#        known_words = list(filter(None, known_words))
        for entry in known_words:
            word = entry['word']
            del entry['word']
            entry['ind'] = self._generate(word)
            entry['known'] = True
            return word, entry
        cache = dict(known_words)
        new_words = filter(lambda w: w not in cache, words)
        for word in new_words:
            riv = self._generate(word)
            cache[word] = {'lex': riv, 'ind': riv, 'known': False}
        self._cache.update(cache)

    def count(self):
        if self._up_to_date:
            return self._count
        else:
            self.get_mean_vector()
            return self._count

    def size(self):
        return self._size

    def _update_words(self, updates):
        self._up_to_date = False
        words = tuple(updates.keys())
        new_words = []
        known_words = []
        for word in words:
            known = word in self
            if known:
                known_words.append(word)
            else:
                new_words.append(word)
        with transaction(self._lex) as tr:
            for word in known_words:
                tr.update({'lex': updates[word]}, where('word') == word)
            for word in new_words:
                tr.insert({'word': word, 'lex': updates[word]})
        for word in words:
            if word in self._cache:
                self._cache[word]['known'] = True

    def _add_lex(self, word, riv):
        if word in self._updates:
            self._updates[word].destructive_add(riv)
        else:
            self._updates[word] = riv

    def update(self, updates):
        for k in updates:
            self._add_lex(k, updates[k])
        if len(self._updates) > self.count() / 10:
            self._update_words(self._updates)

    def _process_context(self, words, context):
        w = map(words.__getitem__, context)
        inds = map(self.get_ind, w)
        return RIV.sum(*inds, size=self._size)

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

    def _process_broken_sentence(self, broken_sentence):
        def processor(index):
            words = broken_sentence[:index] + broken_sentence[index + 1:]
            rivs = map(self.get_lex, words)
            return RIV.sum(*rivs, size=self._size)

        indices = tuple(range(len(broken_sentence)))
        rivs = map(processor, indices)
        return dict(zip(broken_sentence, rivs))

    def ingest_broken(self, broken_text):
        updates = dict()
        sentence_updates = map(self._process_broken_sentence, broken_text)
        for word_update in sentence_updates:
            _merge_update(updates, word_update)
        self.update(updates)

    @staticmethod
    def new(size, nnz, name, db_path=None, overwrite=False):
        db_path = db_path if db_path else "dbs/{}.json".format(name)
        db = _open_db(db_path)
        meta = db.table('metadata')
        lex = db.table('lexicon')
        if len(lex) and not overwrite:
            raise LookupError("{} appears to be an existing lexicon; "
                              "either delete it or try again with a "
                              "new name.".format(name))
        else:
            db.purge_tables()
            db.purge()
            perms = Perms.generate(size)
            meta.insert({'slot': 'size', 'value': size})
            meta.insert({'slot': 'nnz', 'value': nnz})
            meta.insert({'slot': 'name', 'value': name})
            meta.insert({'slot': 'permutations', 'value': perms})
            return lexicon(db)

    @staticmethod
    def open(name, db_path=None):
        db_path = db_path if db_path else "dbs/{}.json".format(name)
        db = _open_db(db_path)
        return lexicon(db)
