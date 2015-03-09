# -*- coding: utf-8 -*-

""" sql.py: provides sql shortcuts to access db """


import re
from copy import copy, deepcopy

class QueryNode:
    
    def __init__(self, name, args, children=[]):
        self.name = name
        self.args = args
        self.children = copy(children)

    def __str__(self):
        return to_sql(parse(self))

    def __or__(self, other):
        assert isinstance(other, QueryNode)
        other.children.append(self)
        return other

    def __xor__(self, other):
        assert isinstance(other, str)
        return self | alias(other)


def qualify_name(alias, col):
    if not col.startswith('@'):
        return col
    col_name = col[1:]
    return alias + '.' + col_name if len(alias) > 0 else col_name

def qualify_string(alias, s):
    return re.sub(r'@[\w]+', lambda m: qualify_name(alias, m.group(0)), s)

def qualify_table(table):
    (name, alias, cols, conds) = table
    return (name, alias, cols, map(lambda s: qualify_string(alias, s), conds))


def parse_single_table(node):

    if node.name == 'table':
        [name, cols] = node.args
        return ([(name, '', cols, [])], [])

    if node.name == 'alias':
        ([(name, _1, cols, conds)], _2) = parse_single_table(node.children[0])
        alias = node.args[0]
        return ([(name, alias, cols, conds)], [])

    if node.name == 'where':
        ([(name, alias, cols, conds)], _) = parse_single_table(node.children[0])
        return ([(name, alias, cols, conds + list(node.args[0]))], [])


def parse_join(node):
    [pk, fk] = node.args

    ([t], _) = parse_single_table(node.children[0])
    table = qualify_table(t)

    pk = qualify_name(table[1], pk)
    
    (tables, joins) = parse(node.children[1])
    if len(tables) == 1:
        [t] = tables
        fk = qualify_name(t[1], fk)
        tables = [qualify_table(t)]
    
    new_join = (pk, qualify_name('', fk))
    return (tables+[table], joins + [new_join])



def parse_modes(node):
    (tables, joins) = parse(node.children[0])
    if len(tables) == 1:
        [t] = tables
        tables = [qualify_table(t)]
    
    selection = []

    if node.name == 'select':
        selection = map(lambda s: qualify_string('', s), node.args[0])

    if node.name == 'update':
        selection = map(lambda (k, v):
                        (qualify_string('', k), qualify_string('', v)), node.args[0])

    return ((node.name, {}), selection, (tables, joins))



def parse_modificator(node):
    ((mode, args), selection, data) = parse_modes(node.children[0])

    if node.name == 'distinct':
        args['distinct'] = True
    
    if node.name == 'order_by':
        order = ('order' in args and args['order']) or []
        args['order'] = order + list(node.args[0])

    if node.name == 'with_pk':
        args['pk'] = node.args[0] 

    
    return ((mode, args), selection, data)


def parse(node):
    if node.name in ['distinct', 'with_pk', 'order_by']:
        return parse_modificator(node)

    if node.name in ['select', 'update']:
        return parse_modes(node)

    if node.name == 'join':
        return parse_join(node)

    if node.name in ['table', 'alias', 'where']:
        return parse_single_table(node)


def to_sql(queue):

    ((mode, args), selection, (tables, joins)) = queue

    fmt_table = lambda (name, alias, _1, _2): name + (' ' + alias if len(alias) > 0 else '')
    fmt_condition = lambda s: '(' + s + ')'
    fmt_join = lambda (key1, key2): '(' + key1 + '=' + key2 + ')'
    fmt_value = lambda (k, v): k + ' = ' + v

    pref_nn = lambda pref, s: pref+s if len(s) > 0 else ''
    

    if mode == 'select':
        order = map(lambda s: qualify_string('', s)
                  , args['order'] if 'order' in args else [])

        return ('select ' + ('distinct ' if 'distinct' in args else '')
                + ', '.join(selection)
                + ' from ' + ', '.join(map(fmt_table, tables))
                + pref_nn(' where ', ' and '.join(
                    map(fmt_join, joins)
                  + map(fmt_condition
                    , sum(map(lambda (_1, _2, _3, conds): conds, tables), []))))
                + pref_nn(' order by ', ', '.join(order)))

    if mode == 'update':
        conds = ''

        if len(tables) == 1:
            conds = re.sub(r'([^\w])%s\.' % tables[0][1], '\\1',
                          pref_nn(' where ', ' and '.join(map(fmt_condition, tables[0][3]))))
        else:
            pk = args['pk']
            conds = (' where %s in (' % qualify_name('', pk)
                      + to_sql((('select', [])
                              , [qualify_name(tables[0][1], pk)]
                              , (tables, joins))) + ')')

        result = ('update ' + tables[0][0]
                  + ' set ' + ', '.join(map(fmt_value, selection))
                  + conds)

        return result
                  


table = lambda name, cols: QueryNode('table', [name, cols])
alias = lambda name: QueryNode('alias', [name])
where = lambda *conds: QueryNode('where', [conds])

join = lambda node, pk, fk: QueryNode('join', [pk, fk], [node])

select = lambda *values: QueryNode('select', [values])
distinct = lambda: QueryNode('distinct', [])
order_by = lambda *values: QueryNode('order_by', [values])

update = lambda *values: QueryNode('update', [values])
with_pk = lambda pk: QueryNode('with_pk', [pk])

q = lambda s: s.replace("'", "''")
 
def execute(db, query):
    p = parse(query)
    ((mode, _1), selection, _2) = p

    if mode == 'select':
        if len(selection) == 1:
            return db.list(to_sql(p))
        return db.all(to_sql(p))

    if mode == 'update':
        db.execute(to_sql(p))
        return
            
