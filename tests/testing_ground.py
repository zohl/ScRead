# -*- coding: utf-8 -*-

import init
import re
from operator import itemgetter

from scread.text.translate import make_translator, use_etymonline
from scread.text.common import get_stem, strip_html, get_page, get_stdout
from scread.gui.style import fmt_header, fmt_entry, fmt_delimiter
from scread.misc.tools import drepr
from scread.misc.delay import delayed 







# print use_etymonline('cash')
# print use_stardict('cat')
# print use_stardict('dog')
# print use_stardict('hitler')
# print use_stardict('pensi')
# print use_stardict('ach')

