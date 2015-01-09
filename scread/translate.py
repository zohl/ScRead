# -*- coding: utf-8 -*-

"""
translate.py: provides functions for P_TRANSLATE parameter. 
Specification:
  In: list of words to translate
  Out: list of translations with preserved order, list of nontranslated words
"""

import subprocess 
from tools import drepr

def ignore(words):
    n = len(words)
    return (['(ignored)'] * n, [])


def sdcv(words):

    res = []
    err = []

    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('-->'))
            , (subprocess.check_output(['sdcv', '-n', word])).split('\n')[1:])

        fmt_header = lambda s: '<p>'+s+'</p>'
        fmt_entry = lambda s: '<p align=left>'+s+'</p>'

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

    res = []
    err = []

    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('        '))
            , (subprocess.check_output(['trans', '-no-ansi', '-t', 'ru', word])))

        fmt_header = lambda s: '<p>'+s+'</p>'
        fmt_entry = lambda s: '<p align=left>'+s+'</p>'

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

