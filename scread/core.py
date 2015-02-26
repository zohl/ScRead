# -*- coding: utf-8 -*-

from aqt import mw
from aqt import addcards
from aqt.utils import showInfo, showWarning, chooseList, askUser, tooltip, closeTooltip
from aqt.qt import *

from anki.utils import intTime
from anki.hooks import addHook, _hooks
from anki.notes import Note

from PyQt4 import QtGui

import re
import time

from interface import conf

from interface import api
from interface.api import dm, ms, tg, db

from interface import queries

from text import translate
from text.core import parse, estimate


def init():
   

    def run_with_warning(f):
        tooltip("Operation has been started, it may take some time. Please, be patient.")
        QtGui.qApp.processEvents()
        
        result = f()

        closeTooltip()
        tooltip("Done!")
        
        return result

    def parse_texts():
        
        (fld_count, fld_context) = map(lambda fld: api.get_field('word', fld), [
            'Count', 'Context'
        ])


        def add_note(word, text_id):
            note = Note(mw.col, api.get_model('word'))
            note.model()['did'] = api.get_deck('words')
            note.fields = [word, str(text_id), '0', '', ''] 
            mw.col.addNote(note)

        def update_note((word, (count, context))):

            note_id = db().scalar("""
            select id
            from notes
            where sfld=?
              and mid=?
            """, word, api.get_model('word')['id'])

            note = mw.col.getNote(note_id)
            note.fields[fld_count] = str(int(note.fields[fld_count]) + count)
            note.fields[fld_context] += context
            note.flush()
            

        def process_text(text_id):

            dictionary = map(str, db().list("""
            select sfld
            from notes
            where mid = ?""", api.get_model('word')['id']))
            
            (new, nfo) = parse(api.get_text(text_id), dictionary) 
            map(lambda word: add_note(word, text_id), new)
            map(update_note, nfo.iteritems()) 


        def main():    
            
            text_ids = db().list("""
            select id
            from notes
            where tags not like '%%%s%%'
              and mid = ? 
            """ % conf.tags['parsed'], api.get_model('text')['id'])


            map(process_text, text_ids)
            mw.col.tags.bulkAdd(text_ids, conf.tags['parsed'])

            # move decent cards to words::unsorted
            db().execute("""
            update cards set
              did = ? 
            where did = ? 
              and ord = ? 
            """, api.get_deck('unsorted'), api.get_deck('words'), api.get_tmpl('word', 'unsorted'))
            

        run_with_warning(main)
        mw.reset()


    def mark_as_known():
        
        #suspend all unsorted cards that weren't checked
        db().execute("""
        update cards set queue = -1
        where did = ?
          and queue = 0
        """, get_deck('unsorted'))
        
        mw.reset()


    def mark_as_new():
        
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


    def supply_cards():

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


    def update_estimations():
        
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



    def init():
        map(api.add_deck, sorted(conf.decks.values(), key = lambda x: len(x['name'])))
        mw.deckBrowser.refresh()

        map(api.add_model, conf.models.values())

        api.add_tags(conf.tags.values())

        
    def drop():
        api.rem_deck('global')
        map(api.rem_model, conf.models.keys())


    def reset():
        if askUser('Reset your ScRead decks?', defaultno=True):
            drop()
            init()


    def create_menu():
        
        queries.test()

        mt = mw.form.menuTools
        menu = mt.addMenu(conf.menu['name'])
        setattr(mt, 'menu'+conf.menu['name'], menu)
       
        def add_menu_item(f):
            action = QAction(conf.menu['items'][f.__name__], mw)
            mw.connect(action, SIGNAL("triggered()"), f)
            menu.addAction(action)
        
        map(add_menu_item, [
          init
        , reset
        , parse_texts
        , mark_as_known
        , mark_as_new
        , supply_cards
        , update_estimations
        ])


    map(lambda f: addHook('profileLoaded', f), [create_menu])
