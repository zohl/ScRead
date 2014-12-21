"""
parse.py: provides functions for P_PARSE parameter. 
Specification: 
  In: text to parse, list of known words
  Out: list of new words, mapping: word -> (count, context)
"""


from anki.notes import Note

from scread import conf

import re


def placeholder(text, dictionary):
    new = []
    nfo = {}
    
    def update_nfo((count, context)):
        return (count + 1, context + 'x')

    def process_word(w):
        if w not in dictionary:
            new.append(w)
        nfo[w] = update_nfo((w in nfo and nfo[w]) or (0, ''))

    words = re.findall(r"[\w']+", text)
    map(process_word, words)
    
    return (new, nfo) 

#TODO
#add deck_id
#- with grouping
#- with synonyms
