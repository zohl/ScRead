# -*- coding: utf-8 -*-

""" translate.py: provides translation methods. """

import re
from operator import itemgetter

from common import get_stem, strip_html, get_page, get_stdout
from scread.gui.style import fmt_header, fmt_entry, fmt_delimiter
from scread.misc.tools import drepr, split_list, with_retry
from scread.misc.delay import delayed 


# block ::= (word, header, [entry])

@with_retry(2)
def make_translator(get_source, parse):

    def result(word):
        pr = lambda (w, _1, _2): get_stem(word) == get_stem(w)
        blocks = []
        try:
            blocks = sorted(filter(pr, parse(get_source(word))))
        except:
            return []
        
        fmt_block = lambda (word, header, entries): ''.join( 
              [fmt_header('%s (%s)' % (word, header))] + map(fmt_entry, entries))
            
        return map(fmt_block, blocks)

    return result



def google_translate_parse(raw):
    raw = raw.split('\n')
    m = re.match(r'(.* (\w+))$', raw[0])
    header_prefix, word = 'Google Translate, ' + m.group(1) + ', ', m.group(2)
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
        return (ls[1][3:], 'Stardict, ' + ls[0][3:], ls[2:])

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



def urban_dictionary_parse(raw):
    elem = lambda name: 'class=[\'"]%s[\'"][^>]*>' % name
    data = lambda name: '(?P<%s>[^<]*)' % name
    
    pattern = '.*?'.join([
        elem('def-panel')
      , elem('def-header'), elem('word'), data('word')
      , elem('meaning'), data('meaning')
      , elem('example'), data('example')
      , elem('contributor'), elem('author'), data('author')
      , elem('def-footer')
      , elem('thumb up'), elem('count'), data('thumb_up')
      , elem('thumb down'), elem('count'), data('thumb_down')])
   
    def make_block(m):
        d = m.groupdict()
        word = d['word']
        header = ('Urban dictionary, by ' +d['author'] +
                 ', rating: +%s -%s' % (d['thumb_up'], d['thumb_down']))
        entries = d['meaning'].split('<br/>') +['--'] + d['example'].split('<br/>')
        
        return (word, header, entries)

    return map(make_block, re.finditer(pattern, raw, flags = re.S))

        
use_urban_dictionary = make_translator(
    lambda w: get_page('http://www.urbandictionary.com/define.php?term='+w)
  , urban_dictionary_parse)



@delayed(0.5)
def translate(word):
    trs = [
        use_stardict
      , use_google_translate
      , use_etymonline
      , use_urban_dictionary]

    return fmt_delimiter().join(sum(map(lambda f: (f(word))[:3], trs), []))
