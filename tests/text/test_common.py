import init 

import re

from scread.tools import drepr
from scread.text.common import get_stem, remove_camel_case, is_bad, iter_words

samples = [
"""
In another moment down went Alice after it, never once considering how in the world she was to get out again. 
""",

"""
So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy- chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.
""",

"""
 Down, down, down. Would the fall never come to an end! `I wonder how many miles I've fallen by this time?' she said aloud. `I must be getting somewhere near the centre of the earth. Let me see: that would be four thousand miles down , I think--' (for, you see, Alice had learnt several things of this sort in her lessons in the schoolroom, and though this was not a very good opportunity for showing off her knowledge, as there was no one to listen to her, still it was good practice to say it over) `--yes, that's about the right distance--but then I wonder what Latitude or Longitude I've got to?' (Alice had no idea what Latitude was, or Longitude either, but thought they were nice grand words to say .) 
"""]



def test_stem_quality():

    words = [
          ['wait', 'waits', 'waited', 'waiting']
        , ['energetic', 'energetically']
        , ['connection', 'connections', 'connective', 'connected', 'connecting']
        , ['note', 'notes', 'notice', 'noticeable']
        , ['black', 'blacken', 'blacked']
        , ['courage', 'courageously', 'courageous', 'courageousness']
        , ['ease', 'easy', 'easiness']
        , ['talk', 'talking', 'talked', 'talkative']
        , ['stormy', 'storminess', 'stormed', 'stormful']
        , ['wealth', 'wealthy', 'wealthiness']
        , ['compete', 'competition', 'competing', 'competitive', 'competed']
    ]

    get_ratio = lambda ws: len(set(map(get_stem, ws)))/float(len(ws))
    result = sum(map(get_ratio, words))/len(words)

    assert result < 0.5



def test_remove_camel_case():
    t_input = ['fooBar', 'fooBarBaz', '123qux', 'quux456']
    t_output = ['foo Bar', 'foo Bar Baz', '123 qux', 'quux 456']
    assert map(remove_camel_case, t_input) == t_output 

    
def test_is_bad():
    t_input = ['123', 'foo', '85893', 'bar']
    t_output = [True, False, True, False]
    assert map(is_bad, t_input) == t_output

   

def test_iter_words():
   
    def test_sample(sample):
        result = []
        map(lambda (sentence, word, stem): result.append(word), iter_words(sample))
        
        s = sample
        for w in result:
            s = s.replace(w, '', 1)
        return None == re.search('[A-Za-z]', s)

    assert map(test_sample, samples) == [True]*len(samples)


