"""
Touch Portal API spec tables

Each lookup table corresponds to a major "collection" in TP SDK,
which are all listed in the TP API Reference page (https://www.touch-portal.com/api/index.php?section=reference)
The tables can be used for generating and/or validating entry.tp files.
Some tables, like for Actions, may contain nested data structures (like Action Data).

Table attributes:
  `v`: minimum TP SDK version
  `r`: required true/false
  `t`: value type (default is str)
  `d`: default value, if any
  `c`: optional list of valid value(s) (choices)
  `l`: lookup table for child data structures, if any
"""

TPSDK_DEFAULT_VERSION = 4

TPSDK_ATTRIBS_SETTINGS = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'name':             { 'v': 3, 'r': True,  't': str },
  'type':             { 'v': 3, 'r': True,  't': str,   'd': "text",        'c': ["text","number"] },
  'default':          { 'v': 3, 'r': False, 't': str },
  'maxLength':        { 'v': 3, 'r': False, 't': int },
  'isPassword':       { 'v': 3, 'r': False, 't': bool },
  'minValue':         { 'v': 3, 'r': False, 't': int },
  'maxValue':         { 'v': 3, 'r': False, 't': int },
  'readOnly':         { 'v': 3, 'r': False, 't': bool,  'd': False },
}

TPSDK_ATTRIBS_STATE = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'id':               { 'v': 1, 'r': True,  't': str },
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "text",        'c': ["text","choice"]},
  'desc':             { 'v': 1, 'r': True,  't': str },
  'default':          { 'v': 1, 'r': True,  't': str,   'd': "" },
  'valueChoices':     { 'v': 1, 'r': False, 't': list },
}

TPSDK_ATTRIBS_EVENT = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'id':               { 'v': 1, 'r': True,  't': str },
  'name':             { 'v': 1, 'r': True,  't': str },
  'format':           { 'v': 1, 'r': True,  't': str },
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "communicate", 'c': ["communicate"] },
  'valueChoices':     { 'v': 1, 'r': True,  't': list,  'd': [] },
  'valueType':        { 'v': 1, 'r': True,  't': str,   'd': "choice" },
  'valueStateId':     { 'v': 1, 'r': True,  't': str },
}

TPSDK_ATTRIBS_ACT_DATA = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'id':               { 'v': 1, 'r': True,  't': str },
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "text",        'c': ["text","number","switch","choice","file","folder","color"] },
  'label':            { 'v': 1, 'r': True,  't': str },
  'default':          { 'v': 1, 'r': True,  't': (str,int,float,bool), 'd': "" },
  'valueChoices':     { 'v': 1, 'r': False, 't': list },
  'extensions':       { 'v': 2, 'r': False, 't': list },
  'allowDecimals':    { 'v': 2, 'r': False, 't': bool },
  'minValue':         { 'v': 3, 'r': False, 't': int },
  'maxValue':         { 'v': 3, 'r': False, 't': int }
}

TPSDK_ATTRIBS_ACTION = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]   [lookup table]
  'id':               { 'v': 1, 'r': True,  't': str },
  'name':             { 'v': 1, 'r': True,  't': str },
  'prefix':           { 'v': 1, 'r': True,  't': str },  # dynamic default? based on category name?
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "communicate", 'c': ["communicate","execute"] },
  'description':      { 'v': 1, 'r': False, 't': str },
  'format':           { 'v': 1, 'r': False, 't': str },  # dynamic replacement of data IDs?
  'executionType':    { 'v': 1, 'r': False, 't': str },
  'execution_cmd':    { 'v': 1, 'r': False, 't': str },
  'tryInline':        { 'v': 1, 'r': False, 't': bool },
  'hasHoldFunctionality': { 'v': 3, 'r': False, 't': bool },
  'data':             { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACT_DATA },
}

TPSDK_ATTRIBS_CONNECTOR = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]   [lookup table]
  'id':               { 'v': 4, 'r': True,  't': str },
  'name':             { 'v': 4, 'r': True,  't': str },
  'format':           { 'v': 4, 'r': False, 't': str },  # dynamic replacement of data IDs?
  'data':             { 'v': 4, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACT_DATA },  # same data as Actions? TP API docs are still vague
}

TPSDK_ATTRIBS_CATEGORY = {
# key name              sdk V   required    [type(s)]    [default value]   [valid value list]   [lookup table]
  'id':               { 'v': 1, 'r': True,  't': str },  # dynamic default id based on plugin id?
  'name':             { 'v': 1, 'r': True,  't': str },
  'imagepath':        { 'v': 1, 'r': False, 't': str },
  'actions':          { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACTION },
  'connectors':       { 'v': 4, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_CONNECTOR },
  'states':           { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_STATE },
  'events':           { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_EVENT },
}

TPSDK_ATTRIBS_ROOT = {
# key name              sdk V   required    [type(s)]    [default value]            [valid value list]   [lookup table]
  'sdk':              { 'v': 1, 'r': True,  't': int,   'd': TPSDK_DEFAULT_VERSION, 'c': [1,2,3,4] },
  'version':          { 'v': 1, 'r': True,  't': int,   'd': 1 },
  'name':             { 'v': 1, 'r': True,  't': str },
  'id':               { 'v': 1, 'r': True,  't': str },
  'configuration':    { 'v': 1, 'r': False, 't': dict },
  'plugin_start_cmd': { 'v': 1, 'r': False, 't': str },
  'settings':         { 'v': 3, 'r': False, 't': list,           'l': TPSDK_ATTRIBS_SETTINGS },
  'categories':       { 'v': 1, 'r': True,  't': list,  'd': [], 'l': TPSDK_ATTRIBS_CATEGORY },
}
