""" conf.py: provides configuration variables for plugin. """


from anki.decks import defaultDeck, defaultConf

from tools import *


beautify = lambda s: ' '.join(map(str.capitalize, s.split('_')))

menu = {
  'name': 'ScRead'
  , 'items': {s:beautify(s) for s in [
      'parse_texts'
    , 'supply_cards'
    , 'update_estimations'
    , 'test'
    ]}
}



#TODO adequate formatting

models = {
    'text': {
        'name': 'ScRead.Text'
        , 'fields': ['Source', 'Text']
        , 'templates': {
            'default': {
                  'name': 'Text.Default'
                , 'qfmt': """
                <p style="align: left">from: {{Source}}</p>
                <pre>{{Text}}</pre>
                """
                , 'afmt': '--'
            }
        }
    },

    'word': {
          'name': 'ScRead.Word'
        , 'fields': ['Word', 'TextId', 'Count', 'Meaning', 'Context']
        , 'templates': {
            'unsorted': {
                  'name': 'Word.Unsorted'
                , 'qfmt': '{{Word}}'
                , 'afmt': '{{Word}}'
            },
            'filtered': {
                  'name': 'Word.Filtered'
                , 'qfmt': '{{Word}}'
                , 'afmt': '{{Meaning}} | {{Context}}'
            }
        }
    }
}


tags = {
    'parsed': 'ScRead.parsed'
  , 'available': 'ScRead.available'
  , 'visible': 'ScRead.visible'
}   

#TODO check configs

make_deck = lambda name, description, conf = None: {
    'name': name
  , 'type': merge(defaultDeck, {'desc': description})
  , 'conf': None if conf is None else merge(defaultConf, conf)
}


decks = {
    'global': make_deck(
          'ScRead'
        , """Global deck for ScRead. There is nothing to do with this deck."""
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
        , """All words"""
        , {
              'new': {'perDay': 0}
            , 'rev': {'perDay': 0}
        }
    ),

    'unsorted': make_deck(
          'ScRead::Words -> Unsorted'
        , """Unsorted words."""
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
        , """Filtered words."""
        , {
              'new': {'perDay': 25}
            , 'rev': {'perDay': 250}
          }
    )
}



