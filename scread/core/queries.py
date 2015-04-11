# -*- coding: utf-8 -*-

""" queries.py: provides queries for plugin's logic. """

from scread.misc.sql import select, update, join, where, distinct, with_pk, order_by
from scread.misc.sql import table, execute, q
from scread.text.common import strip_html

from anki.utils import intTime
#from aqt import mw

import conf
import api

cards = lambda: table('cards', [
    'id', 'nid', 'did', 'ord', 'mod', 'usn', 'type', 'queue', 'due', 'ivl', 'factor'
  , 'reps', 'lapses', 'left', 'odue', 'odid', 'flags', 'data'])

notes = lambda: table('notes', [
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
set_recent = lambda: ('@due', 0)

is_checked = lambda: '@reps > 0'
set_checked = lambda: ('@reps', 1)

stem_is = lambda s: f_stem + " = '" + q(str(s)) +"'"
stem = lambda: '@sfld'

maturity = lambda: 'min(1.0, @ivl*1.0/%d)' % conf.mature_threshold

text_length = lambda: 'length(@flds) - length(@sfld)'
is_empty = lambda: text_length() + ' <= 1'
is_not_empty = lambda: text_length() + ' > 1'

[is_learning, is_suspended, is_buried] = map(
    lambda x: lambda: '@queue = ' + str(x), [0, -1, -2])

[is_not_learning, is_not_suspended, is_not_buried] = map(
    lambda x: lambda: '@queue != ' + str(x), [0, -1, -2])

[set_learning, set_suspended, set_buried] = map(
    lambda x: lambda: ('@queue', str(x)), [0, -1, -2])


words = lambda: notes() | where(model_is('word'))
texts = lambda: notes() | where(model_is('text'))


