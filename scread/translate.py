# -*- coding: utf-8 -*-

"""
translate.py: provides functions for P_TRANSLATE parameter. 

Functions that are visible[1] will be shown in translation methods menu.
Format of a visible function:
  in: list of words to translate
  out: (list of translations (or None) for each word, list of words that weren't translated)
"""

import subprocess 


def ignore(words):
    """ Assigns to each words meaning '(ignored)' """

    n = len(words)
    return (['(ignored)'] * n, [])


def sdcv(words):
    """ Uses stardict console version to translate each word. """

    res = []
    err = []

    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('-->'))
            , (subprocess.check_output(['sdcv', '-n', str(word)])).split('\n')[1:])

        fmt_header = lambda s: '<p class = "header">'+s+'</p>'
        fmt_entry = lambda s: '<p class = "entry">'+s+'</p>'

        fmt = map(lambda s: fmt_entry(s) if (s.startswith(' ')) else fmt_header(s), raw) 
        result = (''.join(fmt)).decode('utf-8')
        
        if len(result) > 0:
            res.append(result)
        else:
            res.append(None)
            err.append(word)
  
    map(process_word, words)
    return (res, err)
   
 

def trans(words):
    """ Uses google translate cli script to translate each word. """

    res = []
    err = []

    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('        '))
            , (subprocess.check_output(['trans', '-no-ansi', '-t', 'ru', str(word)])))

        fmt_header = lambda s: '<p class = "header">'+s+'</p>'
        fmt_entry = lambda s: '<p class = "entry">'+s+'</p>'

        fmt = map(
            lambda s: fmt_entry(s) if (s.startswith(' ')) else fmt_header(s)
            , raw.split('\n')[5:]) 
        
        result = (''.join(fmt)).decode('utf-8')
        
        if len(result) > 0:
            res.append(result)
        else:
            res.append(None)
            err.append(word)
  
    map(process_word, words)
    return (res, err)

