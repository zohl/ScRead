"""
parse.py: provides functions for P_PARSE parameter. 

Format of a function:
  in: text to parse, list of known words
  out: list of new words, dictionary: word -> (count, context)
"""


from scread import conf
from porter import stem
from style import fmt_context, fmt_highlight
from tools import drepr

from anki.utils import stripHTML

import re


def _remove_camel_case(text):
    text = re.sub(r'([a-z])([A-Z])', '\\1 \\2', text)
    text = re.sub(r'([0-9])([a-zA-Z])', '\\1 \\2', text)
    return text

def _is_bad(word):
    return re.match('^[0-9]+', word) is not None;


def with_porter_stemming(text, dictionary):

    text = _remove_camel_case(stripHTML(text))
    
    stems = dict(map(lambda w: (stem(w), w), dictionary))
    new = []
    res = {}

    sentences = re.finditer(r'[^?!.;]+[?!.;]?\n?', text)
   
    for match in sentences:
        sentence = match.group(0)
        
        words = re.finditer(r"[\w]+", sentence)
        for match in words:
            word = match.group(0).lower()
            if _is_bad(word):
                continue

            st = stem(word)
            if st not in stems:
                new.append(word)
                context = re.sub(
                      r'(^|[^\w])(%s)([^\w]|$)' % match.group(0)
                    , '\\1' + fmt_highlight('\\2') + '\\3'
                    , sentence, flags=re.IGNORECASE)
                res[word] = (1, fmt_context(context))

                stems[st] = word
            else:
                w0 = stems[st]
                if w0 in res:
                    (count, context) = res[w0]
                    res[stems[st]] = (count+1, context)
                else:
                    res[w0] = (1, '')
    return (new, res)

