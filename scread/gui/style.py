# -*- coding: utf-8 -*-

""" style.py: provides styling functions and html/css snippets """

from scread.misc.tools import unfold


fmt_header = lambda s: '<p class = "header">'+ s +'</p>'
fmt_entry = lambda s: '<p class = "entry">'+ s +'</p>'
fmt_delimiter = lambda: '<hr/>'
fmt_highlight = lambda s: '<span class = "hl">' + s + '</span>'
fmt_context = lambda s: '<p class = "context">' + s + '</p>'


css = unfold({

      'card': """
              .card {
                font-family: arial;
                font-size: 14px;
                text-align: left;
              }
              """
    
    , 'text': lambda s: s['card'] + """

              .from {
                text-align: left;
                padding-top: 2em;
              }
              """

    , 'word': lambda s: s['card'] + """

              .word {
                font-size: 20px;
                text-align: center;
              }

              .context {
                font-size: 14px;
                text-align: left;
              } 

              .context .hl {
                text-decoration: underline;
              }

              .translation .header {
                text-align: left;
                font-weight: bold;
              }
              
              .translation .entry {
                text-align: left;
              }
              """
})



templates = {
      'text.default': {
            'qfmt': """
                    {{Text}}
                    <p class="from">From: <span>{{Source}}</span></p>
                    """

          , 'afmt': """
                    {{FrontSide}}
                    <hr/>
                    --
                    """ 
    }

    , 'word.unsorted': {
            'qfmt': """
                    <p class = "word">{{Words}}</p>
                    {{Context}}
                    """

          , 'afmt': """
                    {{FrontSide}} 
                    <hr/>
                    --
                    """
    }
    
    , 'word.filtered': {
             'qfmt': """
                     <p class = "word">{{Words}}</p>
                     <p class = "context">{{Context}}</p>
                     """

           , 'afmt': """
                     {{FrontSide}}
                     <hr/>
                     <div class = "translation">{{Translation}}</div>
                     """
    }
}
