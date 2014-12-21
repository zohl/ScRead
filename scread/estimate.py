"""
estimate.py: provides functions for P_ESTIMATE parameter. 
Specification:
  In: list of texts, mapping: words -> [0..1] (estimation of a word familiarity)
  Out: availability of texts in preserved order (boolean value)
"""

import re

def placeholder(texts, estimations):

    def estimate_text(text):
        res = 1
        words = re.findall(r"[\w']+", text)

        for word in words:
            res = res * estimations[word]
        
        return (res > 0.5)

    return map(estimate_text, texts)
