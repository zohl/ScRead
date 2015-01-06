"""
translate.py: provides functions for P_TRANSLATE parameter. 
Specification:
  In: list of words to translate
  Out: list of translations with preserved order, list of nontranslated words
"""

def placeholder(words):
    res = []
    err = []
    
    def f(word):
        if not (word.startswith('a') or word.startswith('e')):
            res.append('word ' + word + ' was successfuly translated')
        else:
            res.append(None)
            err.append(word)

    map(f, words)
    return (res, err)


def only_a(words):
    res = []
    err = []

    def f(word):
        if word.startswith('a'):
            res.append('word ' + word + ' was successfuly translated')
        else:
            res.append(None)
            err.append(word)

    map(f, words)
    return (res, err)


def only_e(words):
    res = []
    err = []

    def f(word):
        if word.startswith('e'):
            res.append('word ' + word + ' was successfuly translated')
        else:
            res.append(None)
            err.append(word)

    map(f, words)
    return (res, err)
