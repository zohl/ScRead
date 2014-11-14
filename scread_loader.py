"""
scread.py: main file for Anki plugin ScRead.
!TODO: description
"""

from scread.core import init
from scread import translate
from scread import estimate

__author__ = "Al Zohali"
__copyright__ = "Copyright 2014, Al Zohali"
__credits__ = []

__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Al Zohali"
__email__ = "zohl@fmap.me"
__status__ = "Prototype"


# Parameters
P_DECK_GLOBAL = 'ScRead'
P_TRANSLATE = translate.placeholder  # See scread/translate.py for options
P_ESTIMATE = estimate.placeholder    # See scread/estimate.py for options
P_THRESHOLD = 0.8

init(P_DECK_GLOBAL, P_TRANSLATE, P_ESTIMATE, P_THRESHOLD)

