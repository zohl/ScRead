import init 

from copy import deepcopy

from scread.misc.tools import *



def test_drepr_short():
    d = {'a': {'aa': 1, 'ab': 2, 'ac': ['aca', 'acb',]}, 'b': {'ba': 5, 'bb': 6}}
    dr = drepr(d)
    assert eval(dr) == d 

def test_drepr_long():
    d = {'num_company_results': 4607, 'start': 0, 'searchresults': [
    {'title': '3D Systems Corporation', 'ticker': 'DDD', 'id': 557960,
    'columns': [{'field': 'MarketCap', 'value': '1.15B'}, {'field':
    'AverageVolume', 'value': 668631}], 'exchange': 'NYSE'},
    {'title': '3M Company', 'ticker': 'MMM', 'id': 24599, 'columns': [
    {'field': 'MarketCap', 'value': '60.79B'}, {'field': 'AverageVolume',
    'value': '3110000'}], 'exchange': 'NYSE'}], 'results_type': 'COMPANY'}
    dr = drepr(d, sort = False)
    assert eval(dr) == d 


data = {
    'foo': 1
  , 'bar': 2
  , 'baz': {
      'qux': 3
    , 'quux': 4
    }
}

data2 = {
      'baz': {
      'qux': 5
    }
}
    

def test_unfold_identity():
    d = deepcopy(data)
    assert unfold(d) == data


def test_unfold_surface():
    d = deepcopy(data)

    # foo = bar*5 + baz.quux*4
    d['foo'] = lambda s: s['bar']*5 + s['baz']['quux']*4

    assert unfold(d)['foo'] == 26


def test_unfold_nested():
    d = deepcopy(data)

    # baz.quux = bar*5 + baz.quux*4
    d['baz']['qux'] = lambda s: s['bar']*5 + s['baz']['quux']*4

    assert unfold(d)['baz']['qux'] == 26 



def _compare(f1, f2, rhs):
    lhs1 = deepcopy(data)
    f1(lhs1, rhs)

    lhs2 = deepcopy(data)
    f2(lhs2, rhs)

    assert lhs1 == lhs2
        

def test_update_surface():
    _compare(
        lambda lhs, rhs: lhs.update(rhs)
      , update
      , {
        'qux': 5
      })


def test_update_nested():
    subrhs = {
        'qux': 5
    }

    _compare(
        lambda lhs, rhs: lhs['baz'].update(subrhs)
      , update
      , {
          'baz': subrhs
      })


def test_merge():
    res = merge(data, data2)
    assert res != data


   
def test_split_list():
    p = lambda n: n > 0
    assert list(split_list(p, [1,2,0,3,4]))           == [[1, 2], [3, 4]]
    assert list(split_list(p, [0,1,2,0,3,4]))         == [[1, 2], [3, 4]]
    assert list(split_list(p, [1,2,0,3,4,0]))         == [[1, 2], [3, 4]]
    assert list(split_list(p, [0,0,1,2,0,0,3,4,0,0])) == [[1, 2], [3, 4]]
