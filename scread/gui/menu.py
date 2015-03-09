# -*- coding: utf-8 -*-

""" menu.py: provides menu config and auxiliary functions """

from aqt import mw
from aqt.qt import QAction, SIGNAL

import re


to_id = lambda s: re.sub(r'[^\w]', '', s.lower().replace(' ', '_'))

def create_item(prefix, root, name, fs):
    action = QAction(name, mw)
    mw.connect(action, SIGNAL("triggered()"), fs[prefix + '_' + to_id(name)])
    root.addAction(action)

def create_submenu(root, name):
    submenu = root.addMenu(name)
    setattr(root, to_id(name), submenu)
    return submenu


def create_menu(prefix, root, items, fs):
    for item in items:
        if isinstance(item, list):
            [subitem, subitems] = item
            submenu = create_submenu(root, subitem)
            create_menu(prefix + '_' + to_id(subitem), submenu, subitems, fs)
        else:
            create_item(prefix, root, item, fs)


def init_menu(items, fs):
    create_menu('', mw.form.menuTools, items, fs)
