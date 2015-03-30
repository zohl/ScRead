# -*- coding: utf-8 -*-

""" translate.py: provides translation methods. """

import re
from operator import itemgetter

from common import get_stem, strip_html, get_page, get_stdout
from scread.gui.style import fmt_header, fmt_entry, fmt_delimiter
from scread.misc.tools import drepr
from scread.misc.delay import delayed 


def make_translator(get_source, parse):

    def result(word):
        pr = lambda (w, _1, _2): get_stem(word) == get_stem(w)
        blocks = []
        try:
            blocks = filter(pr, parse(get_source(word)))
        except:
            return ''

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


use_google_translate = make_translator(
      lambda w: get_stdout('trans', '-no-ansi', '-t', 'ru', str(w))
    , google_translate_parse)




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


use_stardict = make_translator(
      lambda w: get_stdout('sdcv', '-n', str(w))
    , stardict_parse)




def etymonline_parse(raw):
    extract = lambda m: map(lambda i: strip_html(m.group(i)), [1, 2])
    first_word = lambda s: re.match(r' *(\w*)', s.lower()).group(1)
    make_block = lambda h, e: (first_word(h), h, [e])

    return map(lambda m: make_block(*extract(m))
             , re.finditer(r'<dt[^>]*>(.*?)</dt>[^<]*<dd[^>]*>((.|\n)*?)</dd>', raw))


use_etymonline = make_translator(
    lambda w: get_page(
        'http://www.etymonline.com/index.php?allowed_in_frame=0&searchmode=nl&search='
        + get_stem(w)), etymonline_parse)


_choices = dict(sorted(
      filter(lambda (name, _): name.startswith('use_'), locals().items())
    , key = itemgetter(0)))

use_all = delayed(0.3)(lambda word: fmt_delimiter().join(
    filter(lambda s: len(s) > 0
         , map(lambda f: f(word), _choices.values()))))
