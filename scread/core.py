""" core.py: provides init function for the plugin. """

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from anki.hooks import addHook

from tools import drepr
from scread import conf


def init():
   
    def add_text():
        showInfo('adding to ')

    def supply_cards():
        showInfo('suppying cards')

    def update_estimations():
        showInfo('updating estimations')

    def test():
        dm = mw.col.decks


    def create_menu():
        mt = mw.form.menuTools
        menu = mt.addMenu(conf.menu['name'])
        setattr(mt, 'menu'+conf.menu['name'], menu)
       
        def add_menu_item(f):
            action = QAction(conf.menu['items'][f.__name__], mw)
            mw.connect(action, SIGNAL("triggered()"), f)
            menu.addAction(action)
        
        map(add_menu_item, [
          add_text
        , supply_cards
        , update_estimations
        , test
        ])


    def create_decks():
        dm = mw.col.decks
        
        def add_deck(deck):
            if dm.byName(deck['name']) is not None:
                return
            
            if 'conf' in deck and deck['conf'] is not None:
                deck['type']['conf'] = dm.confId(deck['name'], deck['conf'])
                
            dm.id(deck['name'], type = deck['type'])
        
        map(add_deck, sorted(conf.decks.values(), key = lambda x: len(x['name'])))
        mw.deckBrowser.refresh()


    def create_models():
       
        ms = mw.col.models
       
        def add_field(m, field):
            f = ms.newField(field)
            ms.addField(m, f)

        def add_template(m, template):
            t = ms.newTemplate(template['name'])
            t['qfmt'] = template['qfmt']
            t['afmt'] = template['afmt']
            ms.addTemplate(m, t)


        def add_model(model):
            if ms.byName(model['name']) is not None:
                return

            m = ms.new(model['name'])
            map(lambda field: add_field(m, field), model['fields'])
            map(lambda template: add_template(m, template), model['templates'])

            ms.add(m)
        
        map(add_model, conf.models.values())


    map(lambda f: addHook("profileLoaded", f), [
      create_menu
    , create_decks
    , create_models
    ])
