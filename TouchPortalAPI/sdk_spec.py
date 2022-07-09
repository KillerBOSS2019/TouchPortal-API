"""
Touch Portal API spec tables

Each lookup table corresponds to a major "collection" in TP SDK,
which are all listed in the TP API Reference page (https://www.touch-portal.com/api/index.php?section=reference)
The tables can be used for generating and/or validating entry.tp files.
Some tables, like for Actions, may contain nested data structures (like Action Data).

Table attributes:
  - `v`: minimum TP SDK version
  - `r`: required true/false
  - `t`: value type (default is `str`)
  - `d`: default value, if any
  - `c`: optional list of valid value(s) (choices)
  - `l`: lookup table for child data structures, if any

TODO: List valid attribute values per SDK version?
"""

__copyright__ = """
This file is part of the TouchPortal-API project.
Copyright TouchPortal-API Developers
Copyright (c) 2021 Maxim Paperno
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

TPSDK_DEFAULT_VERSION = 6
""" Default Touch Portal SDK version for generating entry.tp JSON. """

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
""" [Settings structure](https://www.touch-portal.com/api/index.php?section=settings) """

TPSDK_ATTRIBS_STATE = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'id':               { 'v': 1, 'r': True,  't': str },
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "text",        'c': ["text","choice"]},
  'desc':             { 'v': 1, 'r': True,  't': str },
  'default':          { 'v': 1, 'r': True,  't': str,   'd': "" },
  "parentGroup":      {"v": 6, "r": False, "t": str},
  'valueChoices':     { 'v': 1, 'r': False, 't': list },
}
""" [State structure](https://www.touch-portal.com/api/index.php?section=states) """

TPSDK_ATTRIBS_EVENT = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]
  'id':               { 'v': 1, 'r': True,  't': str },
  'name':             { 'v': 1, 'r': True,  't': str },
  'format':           { 'v': 1, 'r': True,  't': str },
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "communicate", 'c': ["communicate"] },
  'valueChoices':     { 'v': 1, 'r': True,  't': list,  'd': [] },
  'valueType':        { 'v': 1, 'r': True,  't': str,   'd': "choice",      'c': ["choice"] },
  'valueStateId':     { 'v': 1, 'r': True,  't': str },
}
""" [Event structure](https://www.touch-portal.com/api/index.php?section=events) """

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
""" [Action Data structure](https://www.touch-portal.com/api/index.php?section=action-data) """

TPSDK_ATTRIBS_ACTION = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]   [lookup table]
  'id':               { 'v': 1, 'r': True,  't': str },
  'name':             { 'v': 1, 'r': True,  't': str },
  'prefix':           { 'v': 1, 'r': True,  't': str },  # dynamic default? based on category name?
  'type':             { 'v': 1, 'r': True,  't': str,   'd': "communicate", 'c': ["communicate","execute"] },
  'description':      { 'v': 1, 'r': False, 't': str },
  'format':           { 'v': 1, 'r': False, 't': str },
  'executionType':    { 'v': 1, 'r': False, 't': str },
  'execution_cmd':    { 'v': 1, 'r': False, 't': str },
  'tryInline':        { 'v': 1, 'r': False, 't': bool },
  'hasHoldFunctionality': { 'v': 3, 'r': False, 't': bool },
  'data':             { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACT_DATA },
}
""" [Dynamic Action structure](https://www.touch-portal.com/api/index.php?section=dynamic-actions) """

TPSDK_ATTRIBS_CONNECTOR = {
# key name              sdk V   required    [type(s)]    [default value]    [valid value list]   [lookup table]
  'id':               { 'v': 4, 'r': True,  't': str },
  'name':             { 'v': 4, 'r': True,  't': str },
  'format':           { 'v': 4, 'r': False, 't': str },
  'data':             { 'v': 4, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACT_DATA },  # same data as Actions? TP API docs are still vague
}
""" [Connector structure](https://www.touch-portal.com/api/index.php?section=connectors) """

TPSDK_ATTRIBS_CATEGORY = {
# key name              sdk V   required    [type(s)]  [lookup table]
  'id':               { 'v': 1, 'r': True,  't': str },  # dynamic default id based on plugin id?
  'name':             { 'v': 1, 'r': True,  't': str },  # dynamic default based on plugin name?
  'imagepath':        { 'v': 1, 'r': False, 't': str },
  'actions':          { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_ACTION },
  'connectors':       { 'v': 4, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_CONNECTOR },
  'states':           { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_STATE },
  'events':           { 'v': 1, 'r': False, 't': list, 'l': TPSDK_ATTRIBS_EVENT },
}
""" [Category structure](https://www.touch-portal.com/api/index.php?section=categories) """

TPSDK_ATTRIBS_ROOT = {
# key name              sdk V   required    [type(s)]    [default value]            [valid value list]   [lookup table]
  'sdk':              { 'v': 1, 'r': True,  't': int,   'd': TPSDK_DEFAULT_VERSION, 'c': [1,2,3,4,5,6] },
  'version':          { 'v': 1, 'r': True,  't': int,   'd': 1 },
  'name':             { 'v': 1, 'r': True,  't': str },
  'id':               { 'v': 1, 'r': True,  't': str },
  'configuration':    { 'v': 1, 'r': False, 't': dict },
  'plugin_start_cmd': { 'v': 1, 'r': False, 't': str },
  'plugin_start_cmd_windows': { 'v': 4, 'r': False, 't': str },
  'plugin_start_cmd_linux':   { 'v': 4, 'r': False, 't': str },
  'plugin_start_cmd_mac':     { 'v': 4, 'r': False, 't': str },
  'categories':       { 'v': 1, 'r': True,  't': list,  'd': [], 'l': TPSDK_ATTRIBS_CATEGORY },
  'settings':         { 'v': 3, 'r': False, 't': list,  'd': [], 'l': TPSDK_ATTRIBS_SETTINGS },
}
""" [Plugin structure](https://www.touch-portal.com/api/index.php?section=structure) """
