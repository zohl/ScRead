# -*- coding: utf-8 -*-

""" main.py: provides main function to start plugin """

from aqt import mw
from aqt.utils import showInfo, showWarning, chooseList, askUser, tooltip, closeTooltip

from anki.hooks import addHook

from PyQt4 import QtGui


from scread.core import core
from menu import init_menu 


def run_with_warning(f):
    tooltip("Operation has been started, it may take some time. Please, be patient.")
    QtGui.qApp.processEvents()

    result = f()

    closeTooltip()
    tooltip("Done!")

    return result


items = [['ScRead', [
      'Init'
    , 'Reset'
    , [u'Parse texts…', [
          'all'
        , 'next one'
        , 'next shortest one'
      ]]
    , [u'Mark words…', [
          'as known'
        , 'as unknown'
      ]]
    , [u'Add translations…', [
          'from all available sources'
        , 'from Google Translate'
        , 'from StarDict'
        , 'from Ethymonline'
      ]]
    , 'Update estimations'
    , 'Debug'
    ]
]]


def _scread_init():
    core.init()
    mw.deckBrowser.refresh()

def _scread_reset():
    if askUser('Reset your ScRead decks?', defaultno=True):
        core.reset()
    mw.deckBrowser.refresh()


def _mk_parse_text(f, texts):
    if len(texts) > 0:
        run_with_warning(lambda: f(texts))
        core.populate_unsorted_deck()
        mw.reset()
    else:
        tooltip("There is no new texts.")

def _scread_parse_texts_all():
    _mk_parse_text(lambda texts: map(core.parse_text, texts), core.get_new_texts())

def _scread_parse_texts_next_one():
    _mk_parse_text(lambda texts: core.parse_text(texts[0]), core.get_new_texts(order='date'))
        
def _scread_parse_texts_next_shortest_one():
    _mk_parse_text(lambda texts: core.parse_text(texts[0]), core.get_new_texts(order='size'))

    


def _scread_mark_words_as_known():
    #TODO
    pass

def _scread_mark_words_as_unknown():
    #TODO
    pass

def _scread_add_translations_from_all_available_sources():
    #TODO
    pass

def _scread_add_translations_from_google_translate():
    #TODO
    pass

def _scread_add_translations_from_stardict():
    #TODO
    pass

def _scread_add_translations_from_ethymonline():
    #TODO
    pass

def _scread_update_estimations():
    #TODO
    pass

def _scread_debug():
    #TODO
    pass


fs = dict(filter(lambda (name, _): name.startswith('_scread'), locals().items()))



def main():
    addHook('profileLoaded', lambda: init_menu(items, fs))
