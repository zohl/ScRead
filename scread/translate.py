"""
translate.py: provides functions for P_TRANSLATE parameter. 
Specification:
  In: list of words to translate
  Out: list of translations with preserved order, list of nontranslated words
"""

def placeholder(words):
    return (
          map(lambda w: w + ' is a word or something like that', words)
        , []
    )
    

