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

   

#TODO proper configs

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
          'ScRead::Texts::Available', {

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
          'ScRead::Words::Unsorted', {

          }
    ),

    'filtered': make_filtered_deck(
          'ScRead::Words::Filtered', {

          }
    )
}

 
#sub = lambda s: (lambda self: self['global']['name'] + '::' + s)
#
#decks = unfold({
#  'global': make_deck('ScRead', 'Global desk for ScRead. Do not edit this!', {
#    'new': {'perDay': 9999}
#  , 'rev': {'perDay': 9999}
#  })
#, 'texts': make_deck(sub('Texts'), 'All texts')
#, 'words': make_deck(sub('Words'), 'All words')
#
#    
# , 'words': {
#     'name': make_name('Words')
#   , 'type': make_type({
#        'desc': "All words"
#     })
#   }
#
# , 'available': {
#     'name': make_name('Available')
#   , 'type': make_type({
#        'desc': "Available texts"
#     })
#   , 'conf': make_conf({
#       'name': 'ScRead: available'
#     , 'maxTaken': 900
#     , 'new': {
#         'delays': [
#            1440
#         ,  2880
#         ]
#       , 'perDay': 100
#     }
#     , 'rev': {
#         'perDay': 0
#       }
#     , 'timer': 0
#     })
#   }
#
# , 'filtering': {
#     'name': make_name('Filtering')
#   , 'type': make_type({
#        'desc': "Here you chose words you don't know"
#     })
#   , 'conf': make_conf({
#       'name': 'ScRead: filtering'
#     , 'new': {
#         'delays': [52560000]
#       , 'perDay': 9999
#       }
#     , 'rev': {
#         'perDay': 0
#       }
#     })
#   }
#
# , 'memoizing': {
#     'name': make_name('Memoizing')
#   , 'type': make_type({
#        'desc': "Here you memoize filtered words"
#     })
#   , 'conf': make_conf({
#       'name': 'ScRead: memoize'
#     , 'new': {
#         'perDay': 20
#       }
#     , 'rev': {
#         'perDay': 200
#       }
#     })
#   }
#})


#TODO adequate formatting

models = {
    'text': {
        'name': 'ScRead.Text'
        , 'fields': ['Text', 'Source']
        , 'templates': [
            {
            'name': 'Default'
            , 'qfmt': """
              <p style="align: left">from: {{Source}}</p>
              <pre>{{Text}}</pre>
             """
            , 'afmt': '--'
            }
        ]
    },

    'word': {
          'name': 'ScRead.Word'
        , 'fields': ['Word', 'Meaning', 'Context']
        , 'templates': [
            {
              'name': 'Unsoreted'
            , 'qfmt': '{{Word}}'
            , 'afmt': '--'
            },
            {
              'name': 'Filtered'
            , 'qfmt': '{{Word}}'
            , 'afmt': '{{Meaning}} | {{Context}}'
            }
        ]
    }
}
