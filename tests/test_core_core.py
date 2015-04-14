import init
import os
from scread.misc.tools import drepr
from scread.core import conf 
from scread.core.api import col, dm, ms, tg, db, add_note, get_text, upd_note
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
    text_ids = get_new_texts(order = 'date')
    
    query = (words() | select(f_stem))
    
    parse_text(text_ids[0])
    assert len(execute(db(), query)) == 2
    
    parse_text(text_ids[1])
    assert len(execute(db(), query)) == 4
    
    drop()
    


def test_populate_unsorted_deck():
    init()

    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar foo bar foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz baz baz qux'})
    text_ids = get_new_texts(order = 'date')

    query = (cards() | where(deck_is('unsorted')) | select('*'))
    
    parse_text(text_ids[0])
    assert len(execute(db(), query)) == 0
    populate_unsorted_deck()
    assert len(execute(db(), query)) == 2
    
    parse_text(text_ids[1])
    assert len(execute(db(), query)) == 2
    populate_unsorted_deck()
    assert len(execute(db(), query)) == 4
    
    drop()
    

def test_mark_as():
    init()
    
    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz qux'})
    text_ids = get_new_texts(order = 'date')

    query_unsorted = (cards() | where(deck_is('unsorted'), is_learning()) | select('*'))
    query_known = (cards() | where(deck_is('unsorted'), is_suspended()) | select('*'))
    query_new = (cards() | where(deck_is('unsorted'), is_buried()) | select('*'))

    get_state = lambda: map(lambda query: len(execute(db(), query)), [
         query_unsorted       
       , query_known
       , query_new
    ])


    parse_text(text_ids[0])
    populate_unsorted_deck()
    assert get_state() == [2, 0, 0]

    mark_as('known')
    assert get_state() == [0, 2, 0]


    parse_text(text_ids[1])
    populate_unsorted_deck()
    assert get_state() == [1, 2, 0]

    mark_as('new')
    assert get_state() == [0, 2, 1]
    

    parse_text(text_ids[2])
    populate_unsorted_deck()
    assert get_state() == [1, 2, 1]

    mark_as('known')
    assert get_state() == [0, 3, 1]


    drop()


def test_add_translations():
    init()
    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar baz qux foo'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'qux quux foobar'})
    
    text_ids = get_new_texts()

    p_query_unsorted = lambda: cards() | where(deck_is('unsorted'))

    query_not_suspended = p_query_unsorted() | where(is_not_suspended()) | select('*')
    query_suspended = p_query_unsorted() | where(is_suspended()) | select('*')
    query_filtered = (cards() | where(deck_is('filtered')) | select('*'))

    get_state = lambda: map(lambda query: len(execute(db(), query)), [
         query_not_suspended 
       , query_suspended
       , query_filtered
    ])

    parse_text(text_ids[0])
    populate_unsorted_deck()
    mark_as('new')
    assert get_state() == [4, 0, 0]

    add_translations(lambda x: '<<'+x+'>>' if x != 'bar' else '', lambda: ())
    assert get_state() == [0, 4, 3]


    parse_text(text_ids[1])
    populate_unsorted_deck()
    mark_as('new')
    assert get_state() == [2, 4, 3]

    add_translations(lambda x: '<<'+x+'>>' if x != 'bar' else '', lambda: ())
    assert get_state() == [0, 6, 5]

    drop()


def test_update_estimations():
    init()

    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar'})
    add_note('text', 'texts', {'Source': 'text3', 'Text': 'foo bar baz'})
    add_note('text', 'texts', {'Source': 'text4', 'Text': 'bar baz qux'})
    add_note('text', 'texts', {'Source': 'text5', 'Text': 'baz qux quux'})
    add_note('text', 'texts', {'Source': 'text6', 'Text': 'quux foobar'})
    add_note('text', 'texts', {'Source': 'text7', 'Text': 'foo bar qux'})

    text_ids = get_new_texts()
    skip_duration = int(conf.mature_threshold/3.0)
    
    get_state = lambda: execute(db(), texts() | where(tag_is('available')) | select('count(*)'))[0]


    def process(i, mark = None):
        parse_text(text_ids[i])
        populate_unsorted_deck()
        if mark is not None:
            mark_as(mark)
        add_translations(lambda x: '<<'+x+'>>', lambda: ())
        execute(db(), cards() | update(('@ivl', '@ivl + %d' % skip_duration)))
        update_estimations(lambda: ())

   
    q_all = lambda: words()
    q_checked = lambda: cards() | where(deck_is('unsorted'), is_suspended())
    q_learning = lambda: cards() | where(deck_is('filtered'), is_not_suspended())

    def print_state():
        print map(lambda q: execute(db(), q() | select('count(*)'))[0], [q_all, q_checked, q_learning])

    process(0, 'new')
    assert 0 == get_state()
    process(1, 'known')
    assert 2 == get_state()
    process(2, 'new')
    assert 2 == get_state()
    process(3, 'new')
    assert 3 == get_state()
    process(3, 'new')
    assert 4 == get_state()

    process(4)
    assert 4 == get_state()
    process(5, 'new')
    assert 5 == get_state()
    process(6, 'new')
    assert 7 == get_state()

    drop()


def make_file(name, contents):
    f = open(name, 'w')
    f.write(contents)
    f.close()
    

def test_fetch_file():
    init()
    
    fn = 'test.dat'
    contents = 'foo bar baz qux'
    make_file(fn, contents)

    add_note('text', 'texts', {'Source': fn, 'Text': ''})
    [text_id] = execute(db(), texts() | select('@id'))

    fetch_text(text_id)
    assert get_text(text_id) == contents
    
    os.remove(fn)
    drop()


def test_unfold_batches():
    init()

    files = [
          ('foobar.dat', 'foo bar foo bar')

        , ('foobaz.dat', 'foo baz foo baz')
        , ('fooqux.dat', 'foo qux foo qux')

        , ('barbaz.dat', 'bar baz bar baz')
        , ('barqux.dat', 'bar qux bar qux')
    ]

    map(lambda (fn, cs): make_file(fn, cs), files)

    add_note('batch', 'texts', {'List': '\n'.join(['foobar.dat'])})

    unfold_batches()
    assert 0 == len(execute(db(), batches() | select('@id')))
    assert 1 == len(execute(db(), texts() | select('@id')))

    add_note('batch', 'texts', {'List': '\n'.join(['foobaz.dat', 'fooqux.dat'])})
    add_note('batch', 'texts', {'List': '\n'.join(['barbaz.dat', 'barqux.dat'])})
   
    unfold_batches()
    assert 0 == len(execute(db(), batches() | select('@id')))
    assert 5 == len(execute(db(), texts() | select('@id')))
    
    map(lambda (fn, cs): os.remove(fn), files)
    drop()

test_update_estimations()
