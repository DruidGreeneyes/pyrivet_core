import pytest
from riv.riv import RIV
from mem_lexicon.lexicon import Lexicon


def test_lexicon():
    size = 1000
    nnz = 8
    lexicon = Lexicon(size, nnz)
    token1 = "token1"
    token2 = "token2"
    riv1 = RIV.generate_riv(size, nnz, token1)
    riv2 = RIV.generate_riv(size, nnz, token2)

    # test get_ind
    assert riv1 == lexicon.get_ind(token1)
    assert riv2 == lexicon.get_ind(token2)

    # test add_lex/get_lex
    lexicon.add_lex(token1, riv1)
    assert riv1 * 2 == lexicon.get_lex(token1)

    # test count
    assert lexicon.count() == 1

    # test mean_vector
    assert lexicon.get_lex(token1) == lexicon.get_mean_vector()
    lexicon.add_lex(token2, riv2)
    assert riv1 + riv2 == lexicon.get_mean_vector()

    # test update
    test_tokens = "The quick brown fox jumps over the lazy dog".split(" ")
    updates = dict(zip(test_tokens, map(lexicon.get_ind, test_tokens)))
    lexicon.update(updates)
    assert lexicon.get_lex("The") == lexicon.get_ind("The") * 2

