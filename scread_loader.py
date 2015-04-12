"""
scread.py: main file for Anki plugin ScRead.

ScRead (short for Scrutinized Reading) is a plugin for Anki SRS.

It is a set of tools to help you read texts in a foreign language. 
In a nutshell, it ensures that you know all words in a text before
you read it, and if not, it helps you to memorize them.
"""

from scread.gui.main import main

__author__ = "Al Zohali"
__copyright__ = "Copyright 2014, Al Zohali"
__credits__ = [
    "Martin Porter (http://tartarus.org/~martin/index.html)"
  , "Douglas Harper (http://etymonline.com)"]

__license__ = "GPL"
__version__ = "0.2.0"
__maintainer__ = "Al Zohali"
__email__ = "zohl@fmap.me"
__status__ = "Testing"

main()

