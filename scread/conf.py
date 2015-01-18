""" conf.py: provides configuration variables for plugin. """


from anki.decks import defaultDeck, defaultConf

from tools import *


beautify = lambda s: ' '.join(map(str.capitalize, s.split('_')))

menu = {
  'name': 'ScRead'
  , 'items': {s:beautify(s) for s in [
      'init'
    , 'reset'
    , 'parse_texts'
    , 'supply_cards'
    , 'update_estimations'
    , 'test'
    ]}
}



#TODO adequate formatting

models = {
    'text': {
          'name': 'ScRead.Text'
        , 'css': """
        
        .card {
          font-family: arial;
          font-size: 14px;
          text-align: left;
        }

        .from {
          text-align: left;
          padding-top: 2em;
        }
        """
        , 'fields': ['Source', 'Text']
        , 'templates': {
            'default': {
                  'name': 'Text.Default'
                , 'qfmt': """
                {{Text}}
                <p class="from">From: <span>{{Source}}</span></p>
                """
                , 'afmt': """
                  {{FrontSide}}
                  <hr/>
                  --
                """ 
            }
        }
    },

    'word': {
          'name': 'ScRead.Word'
        , 'css': """
        .card {
          font-family: arial;
          font-size: 14px;
          text-align: left;
        }

        .word {
          font-size: 20px;
          text-align: center;
        }

        .context {
          font-size: 14px;
          text-align: left;
        }
        
        .context .hl {
          font-weight: bold;
        }

        .meaning .header {
          text-align: left;
          font-weight: bold;
        }
        
        .meaning .entry {
          text-align: left;
        }
        """
        , 'fields': ['Word', 'TextId', 'Count', 'Meaning', 'Context']
        , 'templates': {
            'unsorted': {
                  'name': 'Word.Unsorted'
                , 'qfmt': """
                     <p class = "word">{{Word}}</p>
                     <p class = "context">{{Context}}</p>
                  """
                , 'afmt': """
                     {{FrontSide}} 
                     <hr/>
                     --
                  """
            },
            'filtered': {
                  'name': 'Word.Filtered'
                , 'qfmt': """
                     <p class = "word">{{Word}}</p>
                     <p class = "context">{{Context}}</p>
                  """
                , 'afmt': """
                     {{FrontSide}}
                     <hr/>
                     <div class = "meaning">{{Meaning}}</div>
                  """
            }
        }
    }
}


tags = {
    'parsed': 'ScRead.parsed'
  , 'available': 'ScRead.available'
  , 'visible': 'ScRead.visible'
}   


make_deck = lambda name, description, conf = None: {
    'name': name
  , 'type': merge(defaultDeck, {'desc': description})
  , 'conf': None if conf is None else merge(defaultConf, conf)
}


decks = {
    'global': make_deck(
          'ScRead'
        , """Global deck for ScRead. A system deck (don't touch it)."""
        , {
              'new': {'perDay': 9999}
            , 'rev': {'perDay': 9999}
        }
    ),

    'texts': make_deck(
          'ScRead::Texts'
        , """All texts. Here you add texts you want to read."""
        , {
              'new': {'perDay': 0}
            , 'rev': {'perDay': 0}
        }
    ),

    'available': make_deck(
          'ScRead::Texts -> Available'
        , """Available texts."""
        , {
              'new': {
                  'perDay': 10
                  , 'delays': [24*60, 3*24*60]
              }

            , 'rev': {'perDay': 0}
          }
    ),


    'words': make_deck(
          'ScRead::Words'
        , """All words. A system deck (don't touch it)."""
        , {
              'new': {'perDay': 0}
            , 'rev': {'perDay': 0}
        }
    ),

    'unsorted': make_deck(
          'ScRead::Words -> Unsorted'
        , """Unsorted words. Here you check the words you don't know."""
        , {
              'new': {
                  'perDay': 9999
                  , 'delays': [1000*365*24*60, 100*365*24*60]
              }

            , 'rev': {'perDay': 0}
          }
    ),

    'filtered': make_deck(
          'ScRead::Words -> Filtered'
        , """Filtered words. Here you memoize the words."""
        , {
              'new': {'perDay': 25}
            , 'rev': {'perDay': 250}
          }
    )
}



