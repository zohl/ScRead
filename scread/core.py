# -*- coding: utf-8 -*-

""" core.py: provides init function for the plugin. """

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

from tools import drepr
from scread import conf
from scread import translate


def init(P_PARSE, P_TRANSLATE, P_ESTIMATE):
    
    get_model = lambda model: mw.col.models.byName(conf.models[model]['name'])
    get_deck = lambda deck: mw.col.decks.id(conf.decks[deck]['name'])
    get_field = lambda model, field: conf.models[model]['fields'].index(field)

    def get_tmpl(model, tmpl):
        tmpl_name = conf.models[model]['templates'][tmpl]['name']
        predicate = lambda t: t['name'] == tmpl_name 
        return filter(predicate, get_model(model)['tmpls'])[0]['ord']


    def get_text(text_id):
        fld_text = get_field('text', 'Text')
        note = mw.col.getNote(text_id)
        text = note.fields[fld_text]
        return text


    def run_with_warning(f):
        tooltip("Operation has been started, it may take some time. Please, be patient.")
        QtGui.qApp.processEvents()
        
        result = f()

        closeTooltip()
        tooltip("Done!")
        
        return result



    def parse_texts():
        
        db = mw.col.db

        model_text = get_model('text') 
        deck_texts = get_deck('texts')

        model_word = get_model('word')
        deck_words = get_deck('words')
        deck_unsorted = get_deck('unsorted')

        tmpl_unsorted = get_tmpl('word', 'unsorted')

        (fld_count, fld_context) = map(lambda fld: get_field('word', fld), [
            'Count', 'Context'
        ])


        def add_note(word, text_id):
            note = Note(mw.col, model_word)
            note.model()['did'] = deck_words
            note.fields = [word, str(text_id), '0', '', ''] 
            mw.col.addNote(note)

        def update_note((word, (count, context))):

            note_id = db.scalar("""
            select id
            from notes
            where sfld=?
              and mid=?
            """, word, model_word['id'])

            note = mw.col.getNote(note_id)
            note.fields[fld_count] = str(int(note.fields[fld_count]) + count)
            note.fields[fld_context] += context
            note.flush()
            

        def process_text(text_id):

            dictionary = map(str, db.list("""
            select sfld
            from notes
            where mid = ?""", model_word['id']))
            
            (new, nfo) = P_PARSE(get_text(text_id), dictionary) 
            
            map(lambda word: add_note(word, text_id), new)
            map(update_note, nfo.iteritems()) 


        def main():    
            
            text_ids = mw.col.db.list("""
            select id
            from notes
            where tags not like '%%%s%%'
              and mid = ? 
            """ % conf.tags['parsed'], model_text['id'])


            map(process_text, text_ids)
            mw.col.tags.bulkAdd(text_ids, conf.tags['parsed'])

            # move decent cards to words::unsorted
            db.execute("""
            update cards set
              did = ? 
            where did = ? 
              and ord = ? 
            """, deck_unsorted, deck_words, tmpl_unsorted)
            

        run_with_warning(main)
        mw.reset()


    def mark_as_known():
        db = mw.col.db
        
        #suspend all unsorted cards that weren't checked
        db.execute("""
        update cards set queue = -1
        where did = ?
          and queue = 0
        """, get_deck('unsorted'))
        
        mw.reset()


    def mark_as_new():
        db = mw.col.db
        
        #suspend all unsorted cards that weren't checked
        db.execute("""
        update cards set
          queue = -2
        , reps = 1
        , due = ? 
        where did = ?
          and queue = 0
        """, conf.due_threshold, get_deck('unsorted'))
        
        mw.reset()


    def supply_cards():
        db = mw.col.db

        (fld_word, fld_meaning, fld_context) = map(lambda fld: get_field('word', fld), [
            'Word', 'Meaning', 'Context'
        ])

        (deck_words, deck_unsorted, deck_filtered) = map(get_deck, [
            'words', 'unsorted', 'filtered'
        ])

        tmpl_filtered = get_tmpl('word', 'filtered')
        tmpl_unsorted = get_tmpl('word', 'unsorted')


        # select new cards
        notes = db.all("""
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
        """, conf.due_threshold, deck_unsorted)


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

          msg = """Some words cannot be translated:\n  %s\n\nChoose alternative function:"""

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
        db.execute("""
        update cards set
          queue = -1
        , mod = ?
        , usn = ?
        where
            did = ?
        and queue != 0
        and queue != -1
        """, intTime(), mw.col.usn(), deck_unsorted)

        # move decent cards to words::filtered
        db.execute("""
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
                   , intTime(), mw.col.usn(), deck_filtered, tmpl_filtered, deck_words)

        mw.reset()


    def update_estimations():
        db = mw.col.db
        
        deck_texts = get_deck('texts')
        deck_words = get_deck('words')

        model_text = get_model('text') 
        model_word = get_model('word') 

        (deck_unsorted, deck_filtered, deck_texts, deck_available) = map(get_deck, [
            'unsorted', 'filtered', 'texts', 'available'
        ])

        tmpl_unsorted = get_tmpl('word', 'unsorted')
        tmpl_filtered = get_tmpl('word', 'filtered')

        ivl_mature_threshold = 21
        
        text_ids = mw.col.db.list("""
        select id
        from notes
        where tags like "%%%s%%"
          and tags not like "%%%s%%"
          and mid = ?
        """ % (conf.tags['parsed'], conf.tags['available']), model_text['id'])
        
        words = db.all("""
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
            , model_word['id']
            , tmpl_unsorted
            , tmpl_filtered)

        availability = run_with_warning(
            lambda: P_ESTIMATE(map(get_text, text_ids), dict(words)))
       
        fst = lambda (a, b): a
        snd = lambda (a, b): b
        changed_ids = map(fst, filter(snd, zip(text_ids, availability)))
        
        mw.col.tags.bulkAdd(changed_ids, conf.tags['available'])
        
        db.execute("""
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
        """ % conf.tags['available'], deck_available, deck_texts)

        mw.reset()



    def init():

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
                map(lambda template: add_template(m, template), model['templates'].values())
                m['css'] = ('css' in model and model['css']) or ''
                ms.add(m)


            map(add_model, conf.models.values())


        def create_tags():
            mw.col.tags.register(conf.tags.values())

        create_decks()
        create_models()
        create_tags()
        

        
    def drop():
        dm = mw.col.decks
        if get_deck('global') is not None:
            dm.rem(get_deck('global'), childrenToo=True, cardsToo=True)
            
        ms = mw.col.models
        def rem_model(m):
            model = get_model(m) 
            if model is not None:
                ms.rem(model)

        map(rem_model, conf.models.keys())


    def reset():
        if askUser('Reset your ScRead decks?', defaultno=True):
            drop()
            init()


    def create_menu():
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
