# -*- coding: utf-8 -*-

""" core.py: provides core plugin functions """

from anki.utils import intTime
from anki.notes import Note

import re
import time

from scread.text import translate
from scread.text.core import parse, estimate

import conf
import api

from scread.misc.sql import execute 
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


def get_new_texts(order = 'none'):
    # Accepted order values: 'size', 'date'
    query = (texts() | where(tag_is_not('parsed')) | select('@id'))
    if order == 'date': query = (query | order_by('@id'))
    if order == 'size': query = (query | order_by('length(@flds) - length(@sfld)'))
    return execute(api.db(), query)


def parse_text(text_id):
    dictionary = map(str, execute(api.db(), (words() | select(f_stem))))
    (new, nfo) = parse(api.get_text(text_id), dictionary) 

    map(lambda stem: api.add_note('word', 'words', { 
          'Stem': stem
        , 'TextId': str(text_id)
        , 'Count': str(0)
    }), new)

    map(lambda (stem, (count, word, context)): api.upd_note(api.get_note_id('word', stem), {
          'Count': lambda ov: str(int(ov) + count)
        , 'Context': lambda ov: ov + context 
        , 'Word': lambda ov: ov + word
    }), nfo.iteritems())
    
    api.upd_note(text_id, {}, ['parsed'])


def populate_unsorted_deck():
    execute(api.db(), cards
            | where(deck_is('words'), tmpl_is('word', 'unsorted')) 
            | update(set_deck('unsorted')))





def _mark_as_known():

    #suspend all unsorted cards that weren't checked
    db().execute("""
    update cards set queue = -1
    where did = ?
      and queue = 0
    """, get_deck('unsorted'))

    mw.reset()


def _mark_as_new():

    #suspend all unsorted cards that weren't checked
    db().execute("""
    update cards set
      queue = -2
    , reps = 1
    , due = ? 
    where did = ?
      and queue = 0
    """, conf.due_threshold, get_deck('unsorted'))

    mw.reset()


def _supply_cards():

    (fld_word, fld_meaning, fld_context) = map(lambda fld: api.get_field('word', fld), [
        'Word', 'Meaning', 'Context'
    ])

    # select new cards
    notes = db().all("""
    select distinct
      n.id
    , n.sfld
    from
      cards c
    , notes n
    where c.reps > 0
      and c.due <= ?
      and c.did = ? 
      and c.queue != -1
      and c.nid = n.id
    """, conf.due_threshold, api.get_deck('unsorted'))


    def translate_notes():

      def update_note(note_id, meaning):
          note = mw.col.getNote(note_id)
          note.fields[fld_meaning] = meaning
          note.addTag(conf.tags['visible'])
          note.flush()

      (ids, words) = zip(*notes)

      (translated, err) = run_with_warning(lambda: P_TRANSLATE(words))

      choices = filter(lambda s:
            (hasattr(translate.__getattribute__(s), '__call__')) and not s.startswith('_')
          , dir(translate))



      while len(err) > 0:
          res = chooseList(
              re.sub('(.{50,80}) ', '\\1\n', msg % (', '.join(err)))
            , map(lambda s: s.replace('_', ' '), choices))

          p_translate_new = translate.__getattribute__(choices[res])

          (translated_new, err_new) = run_with_warning(lambda: p_translate_new(err))

          i = 0
          for j in range(len(err)):
              while words[i] != err[j]:
                  i += 1
              if len(translated[i]) == 0:
                  translated[i] = translated_new[j]

          err = err_new

      map(lambda xs: update_note(*xs), zip(ids, translated))


    if len(notes) > 0:
        translate_notes()

    # suspend checked cards
    db().execute("""
    update cards set
      queue = -1
    , mod = ?
    , usn = ?
    where
        did = ?
    and queue != 0
    and queue != -1
    """, intTime(), mw.col.usn(), api.get_deck('unsorted'))

    # move decent cards to words::filtered
    db().execute("""
    update cards set 
      queue = 0
    , mod = ?
    , usn = ?
    , did = ?
    where id in (
      select c.id
      from
        cards c
      , notes n
      where c.ord = ?
        and c.did = ?
        and c.nid = n.id
        and n.tags like '%%%s%%'
    )
    """ % conf.tags['visible']
                 , intTime(), mw.col.usn(), api.get_deck('filtered'), api.get_tmpl('word', 'filtered'), api.get_deck('words'))

    mw.reset()


def _update_estimations():

    ivl_mature_threshold = 21

    text_ids = mw.col.db().list("""
    select id
    from notes
    where tags like "%%%s%%"
      and tags not like "%%%s%%"
      and mid = ?
    """ % (conf.tags['parsed'], conf.tags['available']), api.get_model('text')['id'])

    words = db().all("""
    select
      n.sfld, (case 
        when n.tags like '%%%s%%' then min(1.0, cf.ivl*1.0/?)
        when cu.queue = -1        then 1.0
        else                           0.0
      end) as estimation
    from
      notes n
    , cards cu
    , cards cf
    where n.id = cu.nid
      and n.id = cf.nid
      and n.mid = ?
      and cu.ord = ?
      and cf.ord = ?
    """ % conf.tags['visible']
        , str(ivl_mature_threshold)
        , api.get_model('word')['id']
        , api.get_tmpl('word', 'unsorted')
        , api.get_tmpl('word', 'filtered'))

    availability = run_with_warning(
        lambda: estimate(map(api.get_text, text_ids), dict(words)))

    fst = lambda (a, b): a
    snd = lambda (a, b): b
    changed_ids = map(fst, filter(snd, zip(text_ids, availability)))

    mw.col.tags.bulkAdd(changed_ids, conf.tags['available'])

    db().execute("""
    update cards set
      did = ? 
    where id in (
      select c.id
      from
        cards c
      , notes n
      where c.nid = n.id
        and c.did = ?
        and n.tags like '%%%s%%'
    )
    """ % conf.tags['available'], api.get_deck('available'), api.get_deck('texts'))

    mw.reset()







