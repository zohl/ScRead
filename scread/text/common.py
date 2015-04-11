# -*- coding: utf-8 -*-

"""
common.py: provides common functions for 'text' module.
"""

import porter

import urllib2
from HTMLParser import HTMLParser   
import re
import subprocess 


re_sentence = re.compile(r'[^?!.;]+[?!.;]?\n?')
re_word = re.compile(r"[\w]+")


tags_not_text = ['style', 'script', 'object', 'button', 'textarea']

tags_inline = ['b', 'br', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite', 'code',
               'dfn', 'em', 'kbd', 'strong', 'samp', 'var', 'a', 'bdo', 'br', 'q', 'span',
               'sub', 'sup']

tags_blocks = ['dd', 'div', 'p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul',
               'table', 'blockquote']


def strip_html(s):
    blocks = '(' + '|'.join(tags_blocks) + ')'
    return re.sub(r'</?[^<>]*/?>', '',                
                  re.sub(r'(</%s *>)(<%s( [^<>]*)?>)' % (blocks, blocks), r'\1 \3', s, re.I))

get_stem = lambda w: porter.stem(w.lower())


def get_page(url):
    h_redir = urllib2.HTTPRedirectHandler()
    h_cookie = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(h_redir, h_cookie)
    opener.addheaders= [('User-agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')]
    response = opener.open(url)
    h = HTMLParser()
    result = response.read().decode('utf-8', 'ignore')
    return h.unescape(result).replace(' '.decode('utf-8'), ' ')


def get_stdout(*args):
    return subprocess.check_output(args).decode('utf-8').split('\n')


def remove_camel_case(text):
    text = re.sub(r'([a-z])([A-Z])', '\\1 \\2', text)
    text = re.sub(r'([0-9])([a-zA-Z])', '\\1 \\2', text)
    text = re.sub(r'([a-zA-Z])([0-9])', '\\1 \\2', text)
    return text


def is_bad(word):
    return re.match('^[0-9]+', word) is not None;


def iter_words(text):

    sentences = re.finditer(re_sentence, text)

    for match in sentences:
        sentence = match.group(0)
        words = re.finditer(re_word, sentence)

        for match in words:
            word = match.group(0)
            if is_bad(word):
                continue

            stem = get_stem(word)
            
            yield (sentence, word, stem)
