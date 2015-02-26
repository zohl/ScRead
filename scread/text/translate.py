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

from common import get_stem
from scread.interface.style import fmt_header, fmt_entry, fmt_delimiter
from scread.tools import drepr


def make_translator(f_cmdline, f_parse):

    def result(word):
        cmdline = f_cmdline(word)
        raw = subprocess.check_output(cmdline).split('\n')
        blocks = filter(lambda (w, _1, _2): get_stem(word) == get_stem(w), f_parse(raw))

        fmt_block = lambda (_, h, es):  fmt_header(h) +'\n' + '\n'.join(map(fmt_entry, es))
        return '\n\n'.join(map(fmt_block, blocks))

    return result




def google_translate_parse(raw):
    
    m = re.match('^([\w]+)\((.+)\)', raw[5])
    (word, header) = (m.group(1), m.group(2))
    
    blocks = [(word, header, [])]
    
    map(lambda m: blocks.append((word, m.group(1), [m.group(2)]))
      , re.finditer('(\[[\w]+\]),([^\[]*),?'
        , ', '.join(filter(lambda s: len(s) > 0 and not s.startswith('        '), raw[6:]))))
   
    return blocks


def google_translate_cmdline(word):
    return ['trans', '-no-ansi', '-t', 'ru', str(word)]

use_google_translate = make_translator(google_translate_cmdline, google_translate_parse)




def stardict_parse(raw):
    blocks = []

    bs = re.finditer(r'\n([\w]+)\n(( +.*\n)*)'
                   , '\n'.join(filter(lambda s: not s.startswith('-->'), raw[1:])))

    for m in bs:
        word = m.group(1)

        es = re.finditer(r' *([\w]+)? (([0-9]+)?: .*(\n {8}.*)*)', m.group(2))
        entries = []

        for m in es:
            morpheme = m.group(1)
            if morpheme is not None:
                entries.append(morpheme)
            entries.append(m.group(2))
        
        blocks.append((word, word, entries))

    return blocks


def stardict_cmdline(word):
    return ['sdcv', '-n', str(word)]

use_stardict = make_translator(stardict_cmdline, stardict_parse)



_choices = dict(filter(lambda (name, _): name.startswith('use_'), locals().items()))

use_all = lambda word: fmt_delimiter().join(map(lambda f: f(word), choices.values()))
