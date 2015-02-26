# -*- coding: utf-8 -*-

"""
common.py: provides common functions for 'text' module.
"""

import porter
import re


re_sentence = re.compile(r'[^?!.;]+[?!.;]?\n?')
re_word = re.compile(r"[\w]+")


get_stem = lambda w: porter.stem(w.lower())


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
