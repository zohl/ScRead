import init 

from copy import deepcopy

from scread.tools import *


class TestDrepr:

    def test_short(self):
        d = {'a': {'aa': 1, 'ab': 2, 'ac': ['aca', 'acb',]}, 'b': {'ba': 5, 'bb': 6}}
        dr = drepr(d)
        assert eval(dr) == d 

    def test_long(self):
        d = {'num_company_results': 4607, 'start': 0, 'searchresults': [
        {'title': '3D Systems Corporation', 'ticker': 'DDD', 'id': 557960,
        'columns': [{'field': 'MarketCap', 'value': '1.15B'}, {'field':
        'AverageVolume', 'value': 668631}], 'exchange': 'NYSE'},
        {'title': '3M Company', 'ticker': 'MMM', 'id': 24599, 'columns': [
        {'field': 'MarketCap', 'value': '60.79B'}, {'field': 'AverageVolume',
        'value': '3110000'}], 'exchange': 'NYSE'}], 'results_type': 'COMPANY'}
        dr = drepr(d, sort = False)
        assert eval(dr) == d 


class TestUnfold:

    data = {
        'foo': 1
      , 'bar': 2
      , 'baz': {
          'qux': 3
        , 'quux': 4
        }
    }

    
    def test_identity(self):
        d = deepcopy(self.data)
        assert unfold(d) == self.data
        

    def test_surface(self):
        d = deepcopy(self.data)

        # foo = bar*5 + baz.quux*4
        d['foo'] = lambda s: s['bar']*5 + s['baz']['quux']*4

        assert unfold(d)['foo'] == 26

        
    def test_nested(self):
        d = deepcopy(self.data)

        # baz.quux = bar*5 + baz.quux*4
        d['baz']['qux'] = lambda s: s['bar']*5 + s['baz']['quux']*4

        assert unfold(d)['baz']['qux'] == 26 


class TestUpdate:

    lhs = {
        'foo': 1
      , 'bar': 2
      , 'baz': {
          'qux': 3
        , 'quux': 4
        }
    }


    def _compare(self, f1, f2, rhs):
        lhs1 = deepcopy(self.lhs)
        f1(lhs1, rhs)

        lhs2 = deepcopy(self.lhs)
        f2(lhs2, rhs)
        
        assert lhs1 == lhs2
        

    def test_surface(self):
        self._compare(
            lambda lhs, rhs: lhs.update(rhs)
          , update
          , {
            'qux': 5
          })
    

    def test_nested(self):
        subrhs = {
            'qux': 5
        }

        self._compare(
            lambda lhs, rhs: lhs['baz'].update(subrhs)
          , update
          , {
              'baz': subrhs
          })


class TestMerge:
    
    lhs = {
        'foo': 1
      , 'bar': 2
      , 'baz': {
          'qux': 3
        , 'quux': 4
        }
    }
    
    rhs = {
        'baz': {
          'qux': 5
        }
    }

    def test_copying(self):
        res = merge(self.lhs, self.rhs)
        assert res != self.lhs
