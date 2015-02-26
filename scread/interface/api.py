# -*- coding: utf-8 -*-

""" api.py: provides abstraction layer over anki's structures """

from aqt import mw
from anki.utils import stripHTML

from scread.tools import cached
import conf


dm = cached(lambda: mw.col.decks)
ms = cached(lambda: mw.col.models)
tg = cached(lambda: mw.col.tags)
db = cached(lambda: mw.col.db)


get_model = cached(lambda name: ms().byName(conf.models[name]['name']))
get_deck  = cached(lambda name: dm().id(conf.decks[name]['name']))
get_field = cached(lambda model, field: conf.models[model]['fields'].index(field))
get_tag   = cached(lambda name: conf.tags[name])


@cached
def get_tmpl(model, tmpl):
    tmpl_name = conf.models[model]['templates'][tmpl]['name']
    predicate = lambda t: t['name'] == tmpl_name 
    return filter(predicate, get_model(model)['tmpls'])[0]['ord']


def get_text(text_id):
    note = mw.col.getNote(text_id)
    text = note.fields[get_field('text', 'Text')]
    return stripHTML(text)



def add_deck(deck): 

    if dm().byName(deck['name']) is not None:
        return

    if 'conf' in deck and deck['conf'] is not None:
        deck['type']['conf'] = dm().confId(deck['name'], deck['conf'])

    dm().id(deck['name'], type = deck['type'])


def rem_deck(name):
    if get_deck(name) is not None:
        dm().rem(get_deck(name), childrenToo=True, cardsToo=True)



def add_field(m, field):
    f = ms().newField(field)
    ms().addField(m, f)


def add_template(m, template):
    t = ms().newTemplate(template['name'])
    t['qfmt'] = template['qfmt']
    t['afmt'] = template['afmt']
    ms().addTemplate(m, t)


def add_model(model): 

    if ms().byName(model['name']) is not None:
        return

    m = ms().new(model['name'])
    map(lambda field: add_field(m, field), model['fields'])
    map(lambda template: add_template(m, template), model['templates'].values())
    m['css'] = ('css' in model and model['css']) or ''
    ms().add(m)


def rem_model(m):
    model = get_model(m) 
    if model is not None:
        ms().rem(model)


def add_tags(tags):
    tg().register(tags)



#TODO menus



