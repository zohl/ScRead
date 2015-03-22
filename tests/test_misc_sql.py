import init 

import re

from scread.misc.tools import drepr

from scread.misc.sql import *

# customers.snum -> salespeople.snum
# orders.cnum -> customers.cnum
# orders.snum -> salespeople.snum

salespeople = table('salespeople', ['snum', 'sname', 'city', 'comm'])
customers = table('customers', ['cnum', 'cname', 'city', 'rating', 'snum'])
orders = table('orders', ['onum', 'amt', 'odate', 'cnum', 'snum'])


def check_query(regex, q):
    return re.match(regex, str(q)) is not None


def test_sql_select_simple():
    assert check_query(
        r'^select (s\.)?snum, (s.)?sname from salespeople s$'
        , (salespeople ^ 's' | select('@snum', '@sname')))

def test_sql_select_distinct():
    assert check_query(
        r'^select distinct (s\.)?snum, (s.)?sname from salespeople s$'
        , (salespeople ^ 's' | select('@snum', '@sname') | distinct()))

def test_sql_select_where():
    assert check_query(
        r'^select (s\.)?snum, (s.)?sname from salespeople s where \((s\.)?comm > 1000\)$'
        , (salespeople ^ 's' | where('@comm > 1000') | select('@snum', '@sname')))

def test_sql_select_join():
    assert check_query(
        r'^select (c\.)?cname from customers c, salespeople s where \(c\.snum=s\.snum\)$'
        , (customers ^ 'c' | join(salespeople ^ 's', '@snum', '@snum') | select('@cname')))

def test_sql_select_join_parallel():
    assert check_query(
        r'^select (o\.)?amt from orders o, salespeople s, customers c where \(o\.snum=s\.snum\) and \(o\.cnum=c\.cnum\)$'
        , (orders ^ 'o'
           | join(salespeople ^ 's', '@snum', '@snum')
           | join(customers ^ 'c', 'o.cnum', '@cnum')
           | select('@amt')))
   
def test_sql_select_join_nested():
    assert check_query(
          r"select \* from customers c, orders o, salespeople s where \(o\.snum=s\.snum\) and \(c\.cnum=o\.cnum\)"
        , (customers ^ 'c'
           | join(orders ^ 'o'
                  | join(salespeople ^ 's', 'o.snum', '@snum'), '@cnum', 'o.cnum')
           | select('*')))

def test_sql_select_order_by():
    assert check_query(
        r'^select (s\.)?snum, (s.)?sname from salespeople s order by (s.)?city$'
        , (salespeople ^ 's' | select('@snum', '@sname') | order_by('@city')))


def test_sql_update_simple():
    assert check_query(
        r"^update customers set cname = 'Mr\.'\|\|cname$"
        , (customers ^ 'c' | update(('@cname', "'Mr.'||@cname"))))

def test_sql_update_where():
    assert check_query(
        r"^update customers set cname = 'Mr\.'\|\|cname where \(rating > 100\)$"
        , (customers ^ 'c' | where('@rating > 100') | update(('@cname', "'Mr.'||@cname"))))

def test_sql_update_join():
    assert check_query(
        r'update customers set rating = 10 where cnum in \(select c.cnum from customers c, salespeople s where \(c\.snum=s\.snum\) and \(s\.comm = 10\)\)'
        , (customers ^ 'c'
           | join(salespeople ^ 's' | where('@comm = 10'), '@snum', '@snum')
           | update(('@rating', '10'))
           | with_pk('@cnum')))

