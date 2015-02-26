# -*- coding: utf-8 -*-

""" queries.py: provides queries for plugin's logic. """


from scread.sql import table, select, update, execute, join, where, distinct, with_pk


from anki.utils import intTime
from aqt import mw

import conf
import api

cards = table('cards', [
    'id', 'nid', 'did', 'ord', 'mod', 'usn', 'type', 'queue', 'due', 'ivl', 'factor'
  , 'reps', 'lapses', 'left', 'odue', 'odid', 'flags', 'data'])

notes = table('notes', [
    'id', 'guid', 'mid', 'mod', 'usn', 'tags', 'flds', 'sfld', 'csum', 'flags', 'data'])



f_stem = '@sfld'
f_card_pk = '@id'
f_note_pk = '@id'
f_note_fk = '@nid'

model_is = lambda name: '@mid = ' + api.get_model(name)['id']

tag_is = lambda name: "@tags like '%" + api.get_tag(name) + "%'"
tag_is_not = lambda name: "@tags not like '%" + api.get_tag(name) + "%'"

deck_is = lambda name: '@did = ' + str(api.get_deck(name))
set_deck = lambda name: ('@did', str(api.get_deck(name)))

tmpl_is = lambda model, name: '@ord = ' + str(api.get_tmpl(model, name))

is_recent = lambda: '@due <= ' + str(conf.recent_threshold)
set_recent = lambda: ('@due', str(conf.recent_threshold + 1))

is_checked = lambda: '@reps > 0'
set_checked = lambda: ('@reps', 1)

set_activity = lambda: [('@mod', intTime()), ('@usn', mw.col.usn())]

stem_is = lambda s: f_stem + ' = ' + str(s)


[is_learning, is_suspended, is_buried] = map(lambda x: lambda: '@queue = ' + str(x), [0, -1, -2])

[is_not_learning, is_not_suspended, is_not_buried] = map(lambda x: lambda: '@queue != ' + str(x), [0, -1, -2])

[set_learning, set_suspended, set_buried] = map(lambda x: lambda: ('@queue', str(x)), [0, -1, -2])



words = notes | where(model_is('word'))
texts = notes | where(model_is('text'))



def test():
  
  # get note id by word/stem
  (notes ^ 'n' | where(stem_is('word'), model_is('word')) | select(f_note_pk))
  
  # get all stems
  (notes ^ 'n' | where(model_is('word')) | select(f_stem))
  
  
  
  # get not parsed texts
  (notes ^ 'n' 
  | where(tag_is_not('parsed'), model_is('text'))
  | select(f_note_pk))
  
  
  
  #move new words to unsorted deck
  (cards ^ 'c'
  | where(deck_is('words'), tmpl_is('word', 'unsorted'))
  | update(set_deck('unsorted')))
  
  
  
  
  # suspend cards from unsorted deck -> mark as known
  (cards ^ 'c'
  | where(deck_is('unsorted'), is_learning())
  | update(set_suspended))
  
  
  
  
  # mark as unknown
  (cards ^ 'c'
  | where(deck_is('unsorted'), is_learning())
  | update(set_buried, set_checked, set_recent()))
  
  
  
  
  # ???
  (notes ^ 'n'
  | join(cards ^ 'c' | where(is_checked()
                           , is_recent() 
                           , deck_is('unsorted')
                           , is_not_suspended), f_note_fk, f_note_pk)
  | select(f_note_pk, f_stem)
  | distinct())
  
  
  
  # ???
  
  (cards ^ 'c'
      | where(deck_is('unsorted'), is_not_learning, is_not_suspended)
      | update(set_suspended, *set_activity()))
  
  
  
  
  # ??? 
  (cards ^ 'c' | where(tmpl_is('word', 'filtered')
                      , deck_is('words'))
    | join(notes ^ 'n' | where(tag_is('visible')), f_note_pk, f_note_fk)
    | update(set_learning
           , set_deck('filtered')
           , *set_activity())
    | with_pk(f_card_pk))
  
  
  
  
  
  # ???
  (notes ^ 'n'
  | where(tag_is('parsed'), tag_is_not('available'), model_is('text'))
  | select(f_note_pk))
  
  
  #     , api.get_tmpl('word', 'filtered'))
  
  
  # get estimations for notes
  
  estimation_expression = """(case 
    when n.tags like '%%%s%%' then min(1.0, cf.ivl*1.0/?)
    when cu.queue = -1        then 1.0
    else                           0.0
  end) as estimation
  """ % api.get_tag('visible')

  (notes ^ 'n' | where(model_is('word'))
  | join(cards ^ 'cu' | where(tmpl_is('word', 'unsorted')), f_note_fk, f_note_pk)
  | join(cards ^ 'cf' | where(tmpl_is('word', 'filtered')), f_note_fk, f_note_pk)
  | select(f_stem, '<estimation_expression>'))
  
  
  # move cards to available texts deck
  
  (cards ^ 'c' | where(deck_is('texts'))
  | join(notes ^ 'n' | where(tag_is('available')), f_note_pk, f_note_fk)
  | update(set_deck('available'))
  | with_pk(f_card_pk))
  
