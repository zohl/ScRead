"""
estimate.py: provides functions for P_ESTIMATE parameter. 
Specification:
  In: list of texts, mapping: words -> [0..1] (estimation of a word familiarity)
  Out: availability of texts in preserved order (boolean value)
"""

import re
from porter import stem
from tools import drepr

def with_porter_stemming(texts, estimations):
    
    stem_estim = dict(map(lambda (w, e): (stem(str(w)), e), estimations.iteritems()))

    def estimate_text(text):
        words = re.findall(r"[\w']+", text)
        cnts = {}
        
        for w in words:
            st = stem(w)
            cnts[st] = 1 + ((st in cnts and cnts[st]) or 0)

        res = reduce(lambda x, (st, cnt): x*(stem_estim[st]**cnt), cnts.iteritems(), 1)
        return (res > 0.5)

    return map(estimate_text, texts)
