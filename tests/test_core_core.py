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

    add_note('text', 'texts', {'Source': 'text1', 'Text': 'foo bar'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz qux'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz qux quux'})
    add_note('text', 'texts', {'Source': 'text2', 'Text': 'foo bar baz'})

    text_ids = get_new_texts()
    skip_duration = (conf.mature_threshold/3)*2
    
    query_available = (texts() | where(tag_is('available')) | select('*'))

    def process_text(text_id, is_familiar):
        parse_text(text_id)
        populate_unsorted_deck()
        mark_as('known' if is_familiar else 'new')
        add_translations(lambda x: '<<'+x+'>>', lambda: ())
        execute(db(), cards() | update(('@ivl', '@ivl + %d' % skip_duration)))
        update_estimations(lambda: ())

    
    process_text(text_ids[0], False)
    assert len(execute(db(), query_available)) == 1

    process_text(text_ids[1], True)
    assert len(execute(db(), query_available)) == 2

    process_text(text_ids[2], False)
    assert len(execute(db(), query_available)) == 3

    process_text(text_ids[3], False)
    assert len(execute(db(), query_available)) == 4

    drop()
    


