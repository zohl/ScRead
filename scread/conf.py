""" conf.py: provides configuration variables for plugin. """


from anki.decks import defaultDeck, defaultConf, defaultDynamicDeck

from tools import *
from scread import estimate
from scread import translate


# Parameters
P_TRANSLATE = translate.placeholder  # See scread/translate.py for options
P_ESTIMATE = estimate.placeholder    # See scread/estimate.py for options
P_THRESHOLD = 0.8


beautify = lambda s: ' '.join(map(str.capitalize, s.split('_')))

menu = {
  'name': 'ScRead'
  , 'items': {s:beautify(s) for s in [
      'add_text'
    , 'supply_cards'
    , 'update_estimations'
    , 'test'
    ]}
}


    
make_deck = lambda name, description, conf = None: {
    'name': name
  , 'type': merge(defaultDeck, {'desc': description})
  , 'conf': None if conf is None else merge(defaultConf, conf)
}
    

make_filtered_deck = lambda name, conf: {
    'name': name
  , 'type': merge(defaultDynamicDeck, conf)
}

   

#TODO check configs

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

    'available': make_filtered_deck(
          'ScRead::Texts -> Available', {
              'terms': [['deck:"ScRead::Texts" tag:"available"', 9999, 0]]
              , 'delays': [1440*1, 1440*1000*2]
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

    'unsorted': make_filtered_deck(
          'ScRead::Words -> Unsorted', {
              'terms': [['deck:"ScRead::Words" card:"Word.Unsorted"', 9999, 0]]
            , 'delays': [1440*365*1000, 1440*365*100]
          }
    ),

    'filtered': make_filtered_deck(
          'ScRead::Words -> Filtered', {
              'terms': [['deck:"ScRead::Words" card:"Word.Filtered" tag:"visible"', 200, 0]]
          }
    )
}



#TODO adequate formatting

models = {
    'text': {
        'name': 'ScRead.Text'
        , 'fields': ['Text', 'Source', 'Availability']
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
        , 'fields': ['Word', 'TextId', 'Meaning', 'Context']
        , 'templates': {
            'unsorted': {
                  'name': 'Word.Unsorted'
                , 'qfmt': '{{Word}}'
                , 'afmt': '--'
            },
            'filtered': {
                  'name': 'Word.Filtered'
                , 'qfmt': '{{Word}}'
                , 'afmt': '{{Meaning}} | {{Context}}'
            }
        }
    }
}
