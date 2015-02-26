# -*- coding: utf-8 -*-

"""
core.py: provides functions for external interface.
"""

import re

from common import get_stem, remove_camel_case, is_bad, iter_words
from scread.interface.style import fmt_context, fmt_highlight



#TODO: multiple words?
def parse(text, dictionary):
    new = []
    res = {}

    def process_word((sentence, word, stem)):
        if stem in res:
            (count, r_word, context) = res[stem]
            res[stem] = (count+1, r_word, context)
        else:
            if stem not in dictionary:
                new.append(stem)
                
                context = fmt_context(re.sub(
                      r'(^|[^\w])(%s)([^\w]|$)' % word
                    , '\\1' + fmt_highlight('\\2') + '\\3'
                    , sentence, flags=re.IGNORECASE))

                res[stem] = (1, word, context)
            else:
                res[stem] = (1, '', '')

    map(process_word, iter_words(text))
    return (new, res)



def estimate(texts, estim):
    process_text = lambda text: reduce(
          lambda acc, (_1, _2, stem): acc * estim[stem]
        , iter_words(text)
        , 1) > 0.5
    return map(process_text, texts)

