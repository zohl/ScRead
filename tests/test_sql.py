import init 

import re

from scread.sql import *

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
        r'^select (c\.)?cname from customers c, salespeople s where \(s.snum=c.snum\)$'
        , (customers ^ 'c' | join(salespeople ^ 's', '@snum', '@snum') | select('@cname')))

def test_sql_select_join2():
    assert check_query(
        r'^select (o\.)?amt from orders o, salespeople s, customers c where \(s.snum=o.snum\) and \(c.cnum=cnum\)$'
        , (orders ^ 'o'
           | join(salespeople ^ 's', '@snum', '@snum')
           | join(customers ^ 'c', '@cnum', '@cnum')
           | select('@amt')))
    

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
        r'update customers set rating = 10 where cnum in \(select c.cnum from customers c, salespeople s where \(s\.snum=c\.snum\) and \(s\.comm = 10\)\)'
        , (customers ^ 'c'
           | join(salespeople ^ 's' | where('@comm = 10'), '@snum', '@snum')
           | update(('@rating', '10'))
           | with_pk('@cnum')))

