import init 

import re

from scread.misc.tools import drepr
from scread.text.core import parse, estimate


class TestParse():
   
    def test_base(self): 
        t_input = 'foo bar baz qux'
        (new, _) = parse(t_input, []) 
        assert len(new) == len(t_input.split())

    
    def test_non_unique(self): 
        t_input = 'foo bar baz foo bar'
        (new, res) = parse(t_input, []) 
        (count, word, context) = res['foo']

        assert len(new) == len(t_input.split()) - 2
        assert count == 2


    def test_with_dict(self): 
        t_input = 'foo bar baz qux'
        (new, res) = parse(t_input, ['bar', 'qux']) 
        (count, word, context) = res['bar']

        assert len(new) == len(t_input.split()) - 2
        assert count == 1

        
    def test_non_unique_with_dict(self): 
        t_input = 'foo bar baz foo bar'
        (new, res) = parse(t_input, ['bar', 'baz']) 
        (count, word, context) = res['bar']

        assert len(new) == 1
        assert count == 2


class TestEstimate():

    def test_completed(self):
        assert estimate('foo bar baz qux quux', {
              'foo' : 1.0
            , 'bar' : 1.0
            , 'baz' : 1.0
            , 'qux' : 1.0
            , 'quux': 1.0
        }) == True


    def test_incompleted(self):
        assert estimate('foo bar baz foo bar', {
              'foo' : 0.8 
            , 'bar' : 0.8
            , 'baz' : 1.0
        }) == False
