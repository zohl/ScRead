# -*- coding: utf-8 -*-

""" api.py: provides abstraction layer over anki's structures """

import os, tempfile

from anki import Collection 
from anki.utils import stripHTML
from anki.notes import Note


from scread.misc.cache import cached, refresh
from scread.text.common import strip_html

from scread.gui.style import font_size
import conf

from scread.misc.sql import execute
from queries import *


@cached('api')
@refresh('col')
def col():
    try:
        from aqt import mw
        return mw.col
    except:
        (fd, name) = tempfile.mkstemp(suffix=".anki2")
        os.close(fd)
        os.unlink(name)
        return Collection(name)


dm = cached('col')(lambda: col().decks)
ms = cached('col')(lambda: col().models)
tg = cached('col')(lambda: col().tags)
db = cached('col')(lambda: col().db)


get_model = cached('col')(lambda name: ms().byName(conf.models[name]['name']))
get_deck  = cached('col')(lambda name: dm().id(conf.decks[name]['name']))
get_field = cached('col')(lambda model, field: conf.models[model]['fields'].index(field))
get_tag   = cached('col')(lambda name: conf.tags[name])



@cached('col')
def get_tmpl(model, tmpl):
    tmpl_name = conf.models[model]['templates'][tmpl]['name']
    predicate = lambda t: t['name'] == tmpl_name 
    return filter(predicate, get_model(model)['tmpls'])[0]['ord']


def get_text(text_id):
    note = col().getNote(text_id)
    text = note.fields[get_field('text', 'Text')]
    return stripHTML(strip_html(text))


@refresh('col')
def add_deck(deck): 

    if dm().byName(deck['name']) is not None:
        return

    if 'conf' in deck and deck['conf'] is not None:
        deck['type']['conf'] = dm().confId(deck['name'], deck['conf'])

    dm().id(deck['name'], type = deck['type'])


@refresh('col')
def rem_deck(name):
    if get_deck(name) is not None:
        dm().rem(get_deck(name), childrenToo=True, cardsToo=True)



@refresh('col')
def add_field(m, field):
    f = ms().newField(field)
    f['size'] = font_size
    ms().addField(m, f)


@refresh('col')
def add_template(m, template):
    t = ms().newTemplate(template['name'])
    t['qfmt'] = template['qfmt']
    t['afmt'] = template['afmt']
    ms().addTemplate(m, t)


@refresh('col')
def add_model(model): 
    
    is_update = True
    m = ms().byName(model['name'])

    if m is None:
        m = ms().new(model['name'])
        map(lambda field: add_field(m, field), model['fields'])
        ms().setSortIdx(m, 0)
        map(lambda template: add_template(m, template), model['templates'].values())
        is_update = False

    m['css'] = ('css' in model and model['css']) or ''

    if is_update:
        ms().update(m)
    else:
        ms().add(m)



@refresh('col')
def rem_model(m):
    model = get_model(m) 
    if model is not None:
        ms().rem(model)


@refresh('col')
def add_tags(tags):
    tg().register(tags)



def get_note(note_id):
    return col().getNote(note_id)

@cached('col')
def get_note_id(model, sfld):
    [note_id] = execute(db(), notes()
                        | where(model_is(model), "@sfld = '" + q(sfld)+ "'") 
                        | select('@id'))
    return note_id


def add_note(model, deck, flds, tags = []):
    note = Note(col(), get_model(model))
    note.model()['did'] = get_deck(deck)
    note.fields = map(lambda s: (s in flds and flds[s]) or empty_field(), conf.models[model]['fields'])

    map(lambda tag: note.addTag(conf.tags[tag]), tags)
    col().addNote(note)

    

def upd_note(note_id, fields, tags = []):
    def mk_value((f, ov)):
        nv = (f in fields and fields[f]) or None
        return (callable(nv) and nv(ov)) or nv or ov

    note = get_note(note_id)
    model_name = note.model()['name']
    [(model, _1)] = filter(lambda (n, m): m['name'] == model_name, conf.models.iteritems())
    
    note.fields = map(mk_value, zip(conf.models[model]['fields'], note.fields))
    map(lambda tag: note.addTag(conf.tags[tag]), tags)
    note.flush()
