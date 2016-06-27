import sqlite3
import functools
import itertools
import random
from dict_riv import RIV, generate_riv
from vec_perms import Permutations as Perms
from util import cached_function
import os.path
import os

sqlite3.register_adapter(RIV, RIV.to_str)
sqlite3.register_adapter(Perms, Perms.to_str)
sqlite3.register_converter('riv', RIV.from_str)
sqlite3.register_converter('permutations', Perms.from_str)


def _connect(db):
    return sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)


def _create_lexicon(db, size, nnz):
    if size is None or nnz is None:
        raise AssertionError("Cannot create a new lexicon with missing size or nnz.")
    lexicon_creation = "lexicon (word text, lex riv, ind riv)"
    metadata_creation = "metadata (size integer, nnz integer, permutations permutations)"
    with _connect(db) as conn:
        curs = conn.cursor()
        curs.execute("drop table if exists lexicon")
        curs.execute("drop table if exists metadata")
        curs.execute("create table {}".format(lexicon_creation))
        curs.execute("create table {}".format(metadata_creation))
        perms = Perms.generate(size)
        curs.execute("insert into metadata (size, nnz, permutations) values (?, ?, ?)",
                     (size, nnz, perms))


def _open_lexicon(db, size, nnz, overwrite):
    if os.path.isfile(db):
        if overwrite:
            _create_lexicon(db, size, nnz)
    else:
        p = os.path.split(db)[0]
        if not os.path.isdir(p):
            os.mkdir(p)
        _create_lexicon(db, size, nnz)


def _get_metadata(db):
    with _connect(db) as conn:
        return conn.execute("select * from metadata limit 1").fetchone()


def _dictify(entry, columns=()):
    key = entry[0]
    vals = entry[1:]
    if len(columns) != len(vals):
        raise ValueError("Cannot make a dict if cannot match columns and values.")
    d = dict(zip(columns, vals))
    return key, d


def _entrify(dict_entry):
    key, vals = dict_entry
    vals = tuple(vals.values())
    return (key,) + vals


class _local_updates(dict):
    def __init__(self, generator):
        super(_local_updates, self).__init__()
        self.generator = generator

    def __missing__(self, key):
        return self.generator(key)


class Lexicon(object):
    def __init__(self, db_path):
        self._db = db_path
        self._size, self._nnz, self._perms = tuple(_get_metadata(self._db))
        rand = random.Random()
        self._generate = functools.partial(generate_riv, self._size, self._nnz, rand=rand)
        self._cache = {}
        self._updates = {}

    def __enter__(self):
        return self

    def close(self):
        if self._updates:
            self._update_db()

    def __exit__(self, type, value, traceback):
        self.close()

    def _bulk_get(self, words, *columns, conn=None):
        w = tuple(words)
        l = len(words)
        qs = ", ".join(itertools.repeat('?', l))
        query = "select distinct {} from lexicon where word in ({}) limit {}".format(", ".join(columns), qs, l)
        if conn:
            return conn.execute(query, w).fetchall()
        else:
            with _connect(self._db) as c:
                return c.execute(query, w).fetchall()

    def _get(self, word, *columns, conn=None):
        query = "select distinct {} from lexicon where word = ? limit 1".format(", ".join(columns))
        if conn:
            return conn.execute(query, word).fetchone()
        else:
            with _connect(self._db) as c:
                return c.execute(query, word).fetchone()

    def size(self):
        return self._size

    def get_ind(self, word):
        if word in self._cache:
            return self._cache[word]['ind']
        else:
            return self._generate(word)

    def get_lex(self, word):
        if word in self._cache:
            return self._cache[word]['lex']
        else:
            res = self._get(word, 'lex')
            if len(res) > 0:
                return res[0]
            else:
                return self.get_ind(word)

    @cached_function
    def count(self, conn=None):
        c = conn if conn else _connect(self._db)
        res = c.execute("select count(*) from lexicon").fetchone()[0]
        if conn is None:
            c.close()
        return res

    @cached_function
    def get_mean_vector(self):
        print("updating mean vector...")
        with _connect(self._db) as conn:
            count = self.count(conn=conn)
            rivs = conn.execute("select lex from lexicon").fetchall()
            rivs = [r for (r,) in rivs]
            total_riv = RIV.sum(*rivs, size=self._size)
            return total_riv / count

    def _update_local(self, updates):
        for (w, r) in updates.items():
            if w in self._updates:
                self._updates[w]['lex'] += r
            else:
                ind = self.get_ind(w)
                self._updates[w] = {'lex': r, 'ind': ind}
        if len(self._updates) > self.count() / 10:
            self._update_db()

    def _update_db(self):
        print("updating db...")
        self.get_mean_vector.invalidate()
        self.count.invalidate()
        self._cache.update(self._updates)
        words = tuple(self._updates.keys())
        items = self._updates.items()
        with _connect(self._db) as conn:
            found_words = self._bulk_get(words, 'word', conn=conn)
            found_words = [e for (e,) in found_words]
            known_words = []
            new_words = []
            for (w, d) in items:
                if w in found_words:
                    e = (d['lex'], w)
                    known_words.append(e)
                else:
                    e = (w,) + tuple(d.values())
                    new_words.append(e)
            curs = conn.cursor()
            curs.executemany("insert into lexicon (word, lex, ind) values (?, ?, ?)", new_words)
            curs.executemany("update lexicon set lex=? where word=?", known_words)
        self._updates.clear()

    def cache(self, words):
        print("caching {} words...".format(len(words)))
        entries = self._bulk_get(words,'word', 'lex', 'ind')
        dictify = functools.partial(_dictify, columns=('lex', 'ind'))
        cache_entries = map(dictify, entries)
        self._cache.update(dict(cache_entries))
        new_words = filter(lambda w: w not in self._cache, words)
        for word in new_words:
            ind = self._generate(word)
            self._cache[word] = {'lex': ind, 'ind': ind}

    def _process_broken_sentence(self, broken_sentence):
        def processor(index):
            words = broken_sentence[:index] + broken_sentence[index + 1:]
            rivs = map(self.get_ind, words)
            return RIV.sum(*rivs, size=self._size)

        indices = tuple(range(len(broken_sentence)))
        rivs = map(processor, indices)
        return zip(broken_sentence, rivs)

    def ingest_broken_text(self, broken_text):
        updates = _local_updates(self._generate)
        num_sentences = len(broken_text)
        sentence_lengths = map(len, broken_text)
        num_words = sum(sentence_lengths)
        print("Ingesting text: {} sentences, {} words.".format(num_sentences, num_words))
        sentence_updates = map(self._process_broken_sentence, broken_text)
        for sentence_update in sentence_updates:
            for (word, riv) in sentence_update:
                updates[word] += riv
        self._update_local(updates)

    @staticmethod
    def open(db_path="dbs/lexicon.db", size=None, nnz=None, overwrite=False):
        _open_lexicon(db_path, size, nnz, overwrite)
        return Lexicon(db_path)
