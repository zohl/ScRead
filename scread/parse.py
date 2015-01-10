"""
parse.py: provides functions for P_PARSE parameter. 

Format of a function:
  in: text to parse, list of known words
  out: list of new words, dictionary: word -> (count, context)
"""


from scread import conf
from porter import stem

import re


def default(text, dictionary):
    """ Features:
          - detects similar words
          - context is the first sentence with the word
    """

    sentence = r'(^|[^;.!?]*[\W])%s([\W][^;.!?]*|$)'
    
    stems = map(stem, dictionary)
    words = re.findall(r"[\w']+", text)
    new = []
    res = {}


    for w in words:
        st = stem(w)

        if st not in res:
            res[st] = {}

            res[st]['count'] = 0
          
            m = re.search(sentence % w, text)
            res[st]['context'] = m.group(1) + '<strong>' + w + '</strong>' + m.group(2)

            if st not in stems:
                new.append(w)
                res[st]['word'] = w
            else:
                res[st]['word'] = dictionary[stems.index(st)]       


        res[st]['count'] += 1

    fmt = lambda x: (x['word'], (x['count'], x['context']))
    return (new, (dict(map(fmt, res.values()))))

    

