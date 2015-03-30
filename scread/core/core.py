# -*- coding: utf-8 -*-

""" core.py: provides core plugin functions """

from anki.utils import intTime, splitFields
from anki.notes import Note

import re
import time
from operator import itemgetter

from scread.misc.tools import drepr

from scread.text import translate
from scread.text.scrape import scrape
from scread.text.core import parse, estimate

import conf

import api
from api import db, tg, empty_field

from scread.misc.sql import execute 
from scread.misc.delay import dmap 

from queries import *


def init():
    map(api.add_deck, sorted(conf.decks.values(), key = lambda x: len(x['name'])))
    map(api.add_model, conf.models.values())
    api.add_tags(conf.tags.values())


def drop(with_models = False):
    api.rem_deck('global')
    if with_models:
        map(api.rem_model, conf.models.keys())

   
def reset():
    drop(with_models=False)
    init()


def get_empty_texts():
    return execute(db(), texts() | where(is_empty()) | select('@id'))

def fetch_text(text_id):
    [url] = execute(db(), texts() | where('@id = '+str(text_id)) | select('@sfld'))
    if re.match(r' *https?://', url) is not None:
        text = scrape(url)
        api.upd_note(text_id, {'Text': text}, ['fetched'])

def get_new_texts(order = 'none'):
    # Accepted order values: 'size', 'date'
    query = (texts() | where(is_not_empty(), tag_is_not('parsed')) | select('@id'))
    if order == 'date': query = (query | order_by('@id'))
    if order == 'size': query = (query | order_by(text_length()))
    return execute(db(), query)


def parse_text(text_id):
    text = api.get_text(text_id)

    dictionary = map(str, execute(db(), (words() | select(f_stem))))
    (new, nfo) = parse(text, dictionary) 

    map(lambda stem: api.add_note('word', 'words', { 
          'Stem': stem
        , 'TextId': str(text_id)
        , 'Count': str(0)
    }), new)

    map(lambda (stem, (count, word, context)): api.upd_note(api.get_note_id('word', stem), {
          'Count': lambda ov: str(int(ov) + count)
        , 'Context': lambda ov: (ov if ov != empty_field() else '') + context 
        , 'Words': lambda ov: (ov if ov != empty_field() else '') + word
    }), nfo.iteritems())
    
    api.upd_note(text_id, {}, ['parsed'])


def populate_unsorted_deck():
    execute(db(), cards()
            | where(deck_is('words'), tmpl_is('word', 'unsorted')) 
            | update(set_deck('unsorted')))


def mark_as(card_type):
    # Accepted card_type values: 'known', 'new'

    set_state = lambda: ()
    if card_type == 'known': set_state = set_suspended
    if card_type == 'new': set_state = set_buried

    execute(db(), cards()
            | where(deck_is('unsorted'), is_learning())
            | update(
                set_checked()
              , set_recent()
              , set_state()))


def add_translations(f, callback):

    join_words = lambda cs: (words() ^ 'n'
                             | where(tag_is_not('ignored'))
                             | join(cs, f_note_pk, f_note_fk))

    checked_cards = lambda: cards() ^ 'c' | where(
        is_checked()
      , deck_is('unsorted')
      , is_not_suspended())

    new_cards = lambda: checked_cards() | where(is_recent())

    data = execute(db(), join_words(new_cards()) | select('n.id', '@flds'))
    (nids, fss) = zip(*data) or ([], [])
    ws = map(lambda flds: splitFields(flds)[api.get_field('word', 'Words')], fss)
   
    map(lambda (nid, tr): api.upd_note(
          nid
        , {'Translation': tr}
        , [] if len(tr) > 0 else ['ignored'])
        , zip(nids, dmap(f, ws, callback, conf.feedback_time)))

    execute(db(), cards() ^ 'c2' | where(tmpl_is('word', 'filtered'))
            | join(join_words(new_cards()), '@nid', 'n.id')
            | update(set_deck('filtered'), set_recent(), set_learning())
            | with_pk('@id'))

    execute(db(), checked_cards() | update(set_suspended()))
    

def update_estimations(callback):
    text_ids = execute(db(), texts()
                       | where(tag_is('parsed'), tag_is_not('available'))
                       | select('@id'))

    query_all = lambda: words() 
    query_checked = lambda: (words() ^ 'n'
                     | join(cards() ^ 'c' | where(tmpl_is('word', 'unsorted')
                                                , is_suspended()), '@id', '@nid'))

    query_learning = lambda: (words() ^ 'n'
                     | join(cards() ^ 'c' | where(tmpl_is('word', 'filtered')
                                                , is_suspended()), '@id', '@nid'))
    estim = {}
    map(lambda (q, val): estim.update(dict(execute(db(), q() | select(stem(), val)))), [
          (query_all, '0')
        , (query_checked, '1')
        , (query_learning, maturity())
    ])
 
    availability = dmap(lambda text: estimate(text, estim)
                        , map(api.get_text, text_ids)
                        , callback
                        , conf.feedback_time)

    changed_ids = map(itemgetter(0), filter(itemgetter(1), zip(text_ids, availability)))

    tg().bulkAdd(changed_ids, conf.tags['available'])
    
    execute(db(), (cards() ^ 'c'
                   | where(deck_is('texts'))
                   | join(texts() ^ 'n' | where(tag_is('available')), '@nid', '@id')
                   | update(set_deck('available'))
                   | with_pk('@id')))

