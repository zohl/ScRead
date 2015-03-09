import init

from scread.misc.tools import drepr
from scread.core import conf 
from scread.core.api import col, dm, ms, tg, db, add_note
from scread.core.core import *
from scread.core.queries import *

cnt_base_decks = 1
cnt_base_models = 4


def test_sanity():
    assert col() is not None

   
def test_init():
    init()
    assert len(dm().all()) == cnt_base_decks + len(conf.decks)
    assert len(ms().all()) == cnt_base_models + len(conf.models)
    assert len(tg().all()) == len(conf.tags)
    drop()


def test_drop():
    init()
    drop(with_models = True)
    assert len(dm().all()) == cnt_base_decks 
    assert len(ms().all()) == cnt_base_models 


def test_double_init():
    init()
    init()
    assert 1 == 1
    drop()


def test_double_drop():
    init()
    drop(with_models = True)
    drop(with_models = True)
    assert 1 == 1


def test_get_new_texts():
    init()
    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar foo bar foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz baz baz'})
    add_note('text', 'texts', {'Source': 'text3', 'Text': 'foo bar baz qux'})

    assert len(get_new_texts()) == 3
    assert list(reversed(get_new_texts(order = 'date'))) == get_new_texts(order = 'size')
    drop()


def test_parse_text():
    init()
    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar foo bar foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz baz baz qux'})
    query = (words() | select(f_stem))

    text_ids = get_new_texts(order = 'date')
    
    parse_text(text_ids[0])
    assert len(execute(db(), query)) == 2
    
    parse_text(text_ids[1])
    assert len(execute(db(), query)) == 4
    
    drop()
    


def test_populate_unsorted_deck():
    init()

    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar foo bar foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz baz baz qux'})
    query = (cards | where(deck_is('unsorted')) | select('*'))

    text_ids = get_new_texts(order = 'date')
    
    parse_text(text_ids[0])
    assert len(execute(db(), query)) == 0
    populate_unsorted_deck()
    assert len(execute(db(), query)) == 2
    
    parse_text(text_ids[1])
    assert len(execute(db(), query)) == 2
    populate_unsorted_deck()
    assert len(execute(db(), query)) == 4
    
    drop()
    
