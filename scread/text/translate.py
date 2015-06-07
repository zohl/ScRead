# -*- coding: utf-8 -*-

""" translate.py: provides translation methods. """

import re
from operator import itemgetter

from common import get_stem, strip_html, get_page, get_stdout
from scread.gui.style import fmt_header, fmt_entry, fmt_delimiter
from scread.misc.tools import drepr, split_list
from scread.misc.delay import delayed 


# block ::= (word, header, [entry])

def make_translator(get_source, parse):

    def result(word):
        pr = lambda (w, _1, _2): get_stem(word) == get_stem(w)
        blocks = []
        try:
            blocks = sorted(filter(pr, parse(get_source(word))))
        except:
            return ''
        
        fmt_block = lambda (word, header, entries): ''.join( 
              [fmt_header('%s (%s)' % (word, header))] + map(fmt_entry, entries))
            
        return '\n'.join(map(fmt_block, blocks))

    return result



def google_translate_parse(raw):
    raw = raw.split('\n')
    m = re.match(r'(.* (\w+))$', raw[0])
    header_prefix, word = 'Google Translate: ' + m.group(1) + ', ', m.group(2)
    make_block = lambda b: (word, header_prefix + b[0], b[1:][::2])
    return map(make_block,
               split_list(lambda s: len(s) > 0, map(lambda s: s.strip(), raw[2:])))


use_google_translate = make_translator(
      lambda w: get_stdout('trans',
                           '-show-original', 'n',
                           '-show-translation', 'n',
                           '-indent', '4',
                           '-no-ansi', '-t',
                           'ru', str(w)) 
    , google_translate_parse)


def stardict_parse(raw):

    def make_block(b):
        ls = b.split('\n')
        return (ls[1][3:], ls[0][3:], ls[2:])

    return map(lambda m: make_block(m.group(1))
             , re.finditer('(-->.*?-->.*?)(?=-->|$)', raw, flags = re.S))


use_stardict = make_translator(
      lambda w: get_stdout('sdcv', '-n', '--utf8-output', str(w))
    , stardict_parse)



def etymonline_parse(raw):
    extract = lambda m: map(lambda i: strip_html(m.group(i)), [1, 2])
    first_word = lambda s: re.match(r' *(\w*)', s.lower()).group(1)
    make_block = lambda h, e: (first_word(h), 'Etymonline, ' + h, [e])

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
