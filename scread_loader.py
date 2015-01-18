"""
scread.py: main file for Anki plugin ScRead.
!TODO: description
"""

from scread.core import init
from scread import parse, translate, estimate 

__author__ = "Al Zohali"
__copyright__ = "Copyright 2014, Al Zohali"
__credits__ = []

__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Al Zohali"
__email__ = "zohl@fmap.me"
__status__ = "Development"

# Parameters
P_PARSE = parse.with_porter_stemming       # See scread/parse.py for options
P_TRANSLATE = translate.sdcv               # See scread/translate.py for options
P_ESTIMATE = estimate.with_porter_stemming # See scread/estimate.py for options

init(P_PARSE, P_TRANSLATE, P_ESTIMATE)

