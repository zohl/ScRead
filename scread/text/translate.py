# -*- coding: utf-8 -*-

""" translate.py: provides translation methods. """

import re
from operator import itemgetter
from HTMLParser import HTMLParser   

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
            blocks = filter(pr, parse(get_source(word)))
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



class UrbanDictionaryHTMLParser(HTMLParser):
    
    def mk_matchers(conds):
    
        def match_start(self, name, attrs):
            assert(name in conds)
    
            if name not in self._markers:
                if conds[name](attrs):
                    self._markers[name] = 0 + self._depth
                    return True
            else:
                assert(self._markers[name] - self._depth < 0)
                return True
            
            return False
    
            
        def match_end(self, name):
            assert(name in conds)
    
            if name in self._markers:
                if self._markers[name] - self._depth == 0:
                    self._markers.pop(name)
                    return True
    
            return False
    
        return (match_start, match_end)
    
    
    is_class = lambda name: lambda attrs: ('class', name) in attrs

    conds = {       
      'def-panel': is_class('def-panel')
    , 'def-header': is_class('def-header')
    , 'word': is_class('word')
    , 'meaning': is_class('meaning')
    , 'example': is_class('example')
    , 'contributor': is_class('contributor')
    , 'author': is_class('author')
    , 'def-footer': is_class('def-footer')
    , 'thumb-up': is_class('thumb up')
    , 'thumb-down': is_class('thumb down')
    , 'count': is_class('count')
    }

    (_match_start, _match_end) = mk_matchers(conds)

    
    def __init__(self):
        HTMLParser.__init__(self)

        self._markers = {}
        self._depth = 0

        self._buffers = {}
        self._current_buffer = None

        self._blocks = []
        self._current_block = None


    def _append(self, data):
        if self._current_buffer is not None:
            self._buffers[self._current_buffer] += data
       
    def _set_buffer(self, buffer_name):
        if self._current_buffer != buffer_name:
            self._buffers[buffer_name] = ''
            self._current_buffer = buffer_name
        
    def _end_block(self):
        if self._current_block is not None and len(self._current_block) == 6:
            self._blocks.append(self._current_block)
            self._markers.clear()
            self._current_block = None


    def handle_starttag(self, tag, attrs):
        self._depth += 1
        self._append('<%s>' % tag)
        
        if self._match_start('def-panel', attrs):

            if self._current_block is None:
                self._current_block = {}

            if self._match_start('def-header', attrs):
                if self._match_start('word', attrs):
                    self._set_buffer('word')

            if self._match_start('meaning', attrs):
                self._set_buffer('meaning')

            if self._match_start('example', attrs):
                self._set_buffer('example')
                
            if self._match_start('contributor', attrs):
                if self._match_start('author', attrs):
                    self._set_buffer('author')

            if self._match_start('def-footer', attrs):
                if self._match_start('thumb-up', attrs):
                    if self._match_start('count', attrs):
                        self._set_buffer('thumb-up')

                if self._match_start('thumb-down', attrs):
                    if self._match_start('count', attrs):
                        self._set_buffer('thumb-down')


    def handle_endtag(self, tag):

        if self._match_end('def-panel'): pass

        if self._match_end('def-header'): pass
        if self._match_end('word'):
            self._current_block['word'] = self._buffers['word']

        if self._match_end('meaning'): 
            self._current_block['meaning'] = self._buffers['meaning']

        if self._match_end('example'): 
            self._current_block['example'] = self._buffers['example']

        if self._match_end('contributor'): pass
        if self._match_end('author'): 
            self._current_block['author'] = self._buffers['author']


        if self._match_end('def-footer'): pass

        if self._match_end('thumb-up'): pass
        if self._match_end('thumb-down'): pass

        if self._match_end('count'): 
            if 'thumb-up' in self._markers:
                self._current_block['thumb-up'] = self._buffers['thumb-up']
            if 'thumb-down' in self._markers:
                self._current_block['thumb-down'] = self._buffers['thumb-down']

        self._depth -= 1
        self._append('</%s>' % tag)

        self._end_block()

    def handle_data(self, data):
        self._append(data)



def urban_dictionary_parse(raw):
   
    def format_block(b):
        word = b['word']
        header = ('Urban dictionary, by ' +b['author'] +
                 ', rating: +%s -%s' % (b['thumb-up'], b['thumb-down']))

        entries = b['meaning'].split('<br/>') +['--'] + b['example'].split('<br/>')
        clear_entry = lambda s: re.sub('(\n|</?[^>]+>)', '', s)
        return (word, header, map(clear_entry, entries))

    parser = UrbanDictionaryHTMLParser()
    parser.feed(raw)
    parser.close()
    sort_key = lambda x, y: (x - y)/(1 + x + y)
    blocks = sorted(parser._blocks
                  , key = lambda b: sort_key(float(b['thumb-up']), float(b['thumb-down'])))

    return map(format_block, parser._blocks)

        
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
