"""
parse.py: provides functions for P_PARSE parameter. 

Format of a function:
  in: text to parse, list of known words
  out: list of new words, dictionary: word -> (count, context)
"""


from scread import conf
from porter import stem

import re


def with_porter_stemming(text, dictionary):

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
            res[st]['context'] = '<p class = "context">' + m.group(1) + '<span class = "hl">' + w + '</span>' + m.group(2) +'</p>'

            if st not in stems:
                new.append(w)
                res[st]['word'] = w
            else:
                res[st]['word'] = dictionary[stems.index(st)]       


        res[st]['count'] += 1

    fmt = lambda x: (x['word'], (x['count'], x['context']))
    return (new, (dict(map(fmt, res.values()))))

    

