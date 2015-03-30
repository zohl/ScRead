# -*- coding: utf-8 -*-

""" main.py: provides main function to start plugin """

from aqt import mw
from aqt.utils import showInfo, showWarning, chooseList, askUser, tooltip, closeTooltip

from anki.hooks import addHook

from PyQt4 import QtGui

from scread.text import translate 

from scread.core import conf
from scread.core import core
from scread.misc.delay import dmap 

from menu import init_menu 


def immediate_message(msg):
    tooltip(msg)
    QtGui.qApp.processEvents()

show_progress = lambda i, n: immediate_message('Progress: %d/%d' % (i, n))
show_done = lambda: tooltip('Done!')


items = [['&ScRead', [
      '&Init'
    , [u'&Texts…', [
          '&fetch from web'
        , '--'
        , '&parse all'
        , 'parse &next one'
        , 'parse next &shortest one'
        , '--'
        , '&update estimations'
      ]]
    , [u'&Words…', [
          '&add translations'
        , '--'
        , '&mark as known'
        , 'mark as &new'
      ]]
    , '--'
    , '&Reset'
    ]
]]


def _scread_init():
    core.init()
    mw.deckBrowser.refresh()

def _scread_reset():
    if askUser('Reset your ScRead decks?', defaultno=True):
        core.reset()
    mw.deckBrowser.refresh()


def _scread_texts_fetch_from_web():
    texts = core.get_empty_texts()
    if len(texts) > 0:
        dmap(core.fetch_text, texts, show_progress, conf.feedback_time) 
    else:
        tooltip('There is no links.')

def _mk_parse_text(f, texts):
    if len(texts) > 0:
        f(texts)
        core.populate_unsorted_deck()
        mw.reset()
        show_done()
    else:
        tooltip("There is no new texts.")

def _scread_texts_parse_all():
    _mk_parse_text(lambda texts: dmap(core.parse_text
                                    , texts
                                    , show_progress
                                    , conf.feedback_time)
                 , core.get_new_texts())

def _scread_texts_parse_next_one():
    _mk_parse_text(lambda texts: core.parse_text(texts[0]), core.get_new_texts(order='date'))
        
def _scread_texts_parse_next_shortest_one():
    _mk_parse_text(lambda texts: core.parse_text(texts[0]), core.get_new_texts(order='size'))

    

def _scread_texts_update_estimations():
    core.update_estimations(show_progress)
    mw.reset()
    show_done()


def _scread_words_add_translations():
    core.add_translations(translate.use_all, show_progress)
    mw.reset()
    show_done()

def _scread_words_mark_as_known():
    core.mark_as('known')
    mw.reset()

def _scread_words_mark_as_new():
    core.mark_as('new')
    mw.reset()



fs = dict(filter(lambda (name, _): name.startswith('_scread'), locals().items()))



def main():
    addHook('profileLoaded', lambda: init_menu(items, fs))
