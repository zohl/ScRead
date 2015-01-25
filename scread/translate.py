# -*- coding: utf-8 -*-

"""
translate.py: provides functions for P_TRANSLATE parameter. 

Functions that are visible[1] will be shown in translation methods menu.
Format of a visible function:
  in: list of words to translate
  out: (list of translations (or empty strings) for each word
      , list of words that weren't translated)
"""

import subprocess 
import re

import porter
import style 


def ignore(words):
    """ Assigns to each words meaning '(ignored)' """

    n = len(words)
    return ([style.fmt_entry('(ignored)')] * n, [])


def sdcv(words):
    """ Uses stardict console version to translate each word. """

    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('-->'))
            , (subprocess.check_output(['sdcv', '-n', str(word)])).split('\n')[1:])

        # group by headers
        trs = []

        header = ''
        entry = ''

        for line in raw:
            if line.startswith('  '):
                entry += line.strip()
            else:
                if len(header) > 0:
                    trs.append((header, entry))
                header = line.strip()
                entry = ''

        if len(header) > 0:
            trs.append((header, entry))
           
 
        # drop not related
        res = ''

        for (header, entry) in trs:
            if porter.stem(header.lower()) != porter.stem(word):
                continue
            res += style.fmt_header(header)
            res += ''.join(map(style.fmt_entry,
                               re.sub(' *([0-9]+:)', '\n\\1', entry).split('\n')))

        return res.decode('utf-8')


    res = []
    err = [] 
   
    for word in words:
        result = process_word(word)
        res.append(result)
        if len(result) == 0:
            err.append(word)

    return (res, err)

   
 

def trans(words):
    """ Uses google translate cli script to translate each word. """
    res = []
    err = []   
    
    def process_word(word):
        raw = filter(
              lambda s: len(s) > 0 and not (s.startswith('        '))
            , (subprocess.check_output(
                ['trans', '-no-ansi', '-t', 'ru', str(word)])).split('\n'))
       
        default = raw[0]

        # group by headers
        trs = []

        header = ''
        entry = ''

        for line in raw[5:]:
            if line.startswith('  '):
                entry += line.strip() + ', '
            else:
                if len(header) > 0:
                    trs.append((header, entry))
                header = line.strip()
                entry = ''

        if len(header) > 0:
            trs.append((header, entry))
     
        # putting all together
        res = ''
        if len(trs) > 0:
            res += style.fmt_entry(default)
            res += ''.join(map(lambda (header, entry):
                               style.fmt_header(header) + style.fmt_entry(entry[:-2]), trs))

        return res.decode('utf-8')


    for word in words:
        result = process_word(word)
        res.append(result)
        if len(result) == 0:
            err.append(word)

    return (res, err)


