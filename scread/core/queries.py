# -*- coding: utf-8 -*-

""" queries.py: provides queries for plugin's logic. """

from scread.misc.sql import select, update, join, where, distinct, with_pk, order_by
from scread.misc.sql import table, execute, q


from anki.utils import intTime
#from aqt import mw

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

tag_is = lambda name: "@tags like '%" + q(api.get_tag(name)) + "%'"
tag_is_not = lambda name: "@tags not like '%" + q(api.get_tag(name)) + "%'"

deck_is = lambda name: '@did = ' + str(api.get_deck(name))
set_deck = lambda name: ('@did', str(api.get_deck(name)))

tmpl_is = lambda model, name: '@ord = ' + str(api.get_tmpl(model, name))

is_recent = lambda: '@due <= ' + str(conf.recent_threshold)
set_recent = lambda: ('@due', str(conf.recent_threshold + 1))

is_checked = lambda: '@reps > 0'
set_checked = lambda: ('@reps', 1)

# set_activity = lambda: [('@mod', intTime()), ('@usn', mw.col.usn())]

stem_is = lambda s: f_stem + " = '" + q(str(s)) +"'"


[is_learning, is_suspended, is_buried] = map(lambda x: lambda: '@queue = ' + str(x), [0, -1, -2])

[is_not_learning, is_not_suspended, is_not_buried] = map(lambda x: lambda: '@queue != ' + str(x), [0, -1, -2])

[set_learning, set_suspended, set_buried] = map(lambda x: lambda: ('@queue', str(x)), [0, -1, -2])



words = lambda: notes | where(model_is('word'))
texts = lambda: notes | where(model_is('text'))





#def test():
#  
#  words = notes | where(model_is('word'))
#  texts = notes | where(model_is('text'))
#  
#  unsorted_word_cards = cards | where(deck_is('unsorted'))
#  filtered_word_cards = cards | where(deck_is('filtered'))
#  new_word_cards      = cards | where(deck_is('words'))
# 
#  text_cards = cards | where(deck_is('texts'))
#  
#  
#  # get note id by word/stem
#  (words | where(stem_is('<word>')) | select(f_note_pk))
#  
#  # get all stems
#  (words | select(f_stem))
#  
#  # get not parsed texts
#  (texts | where(tag_is_not('parsed')) | select(f_note_pk))
#  
#  #move new words to unsorted deck
#  (new_word_cards | where(tmpl_is('word', 'unsorted')) | update(set_deck('unsorted')))
#  
#  # suspend cards from unsorted deck -> mark as known
#  (unsorted_word_cards | where(is_learning()) | update(set_suspended))
#  
#  # mark as unknown
#  (unsorted_word_cards | where(is_learning()) | update(set_buried, set_checked, set_recent()))
#  
#  
#  # ???
#  (notes ^ 'n'
#  | join(unsorted_word_cards ^ 'c' 
#        | where(is_checked()
#              , is_recent() 
#              , is_not_suspended), f_note_fk, f_note_pk)
#  | select(f_note_pk, f_stem)
#  | distinct())
# 
# 
#  # ???
#  (unsorted_word_cards ^ 'c'
#  | where(is_not_learning, is_not_suspended)
#  | update(set_suspended, *set_activity()))
#  
#  
#  # ??? 
#  (new_word_cards ^ 'c'
#  | where(tmpl_is('word', 'filtered'))
#  | join(notes ^ 'n' | where(tag_is('visible')), f_note_pk, f_note_fk)
#  | update(set_learning, set_deck('filtered'), *set_activity())
#  | with_pk(f_card_pk))
#  
#  
#  # ???
#  (texts | where(tag_is('parsed'), tag_is_not('available')) | select(f_note_pk))
#  
#  
#  # ???
#  estimation_expression = """(case 
#    when n.tags like '%%%s%%' then min(1.0, cf.ivl*1.0/?)
#    when cu.queue = -1        then 1.0
#    else                           0.0
#  end) as estimation
#  """ % api.get_tag('visible')
#
#  (words ^ 'n'  
#  | join(cards ^ 'cu' | where(tmpl_is('word', 'unsorted')), f_note_fk, f_note_pk)
#  | join(cards ^ 'cf' | where(tmpl_is('word', 'filtered')), f_note_fk, f_note_pk)
#  | select(f_stem, '<estimation_expression>'))
# 
#  
#  # move cards to available texts deck
#  
#  (text_cards ^ 'c' 
#  | join(notes ^ 'n' | where(tag_is('available')), f_note_pk, f_note_fk)
#  | update(set_deck('available'))
#  | with_pk(f_card_pk))
  
