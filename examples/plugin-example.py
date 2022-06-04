"""
Touch Portal Plugin Example
"""

import sys

# Load the TP Python API. Note that TouchPortalAPI must be installed (eg. with pip)
# _or_ be in a folder directly below this plugin file.
import TouchPortalAPI as TP

# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)


# Version string of this plugin (in Python style).
__version__ = "1.0"

# The unique plugin ID string is used in multiple places.
# It also forms the base for all other ID strings (for states, actions, etc).
PLUGIN_ID = "tp.plugin.example.python"

## Start Python SDK declarations
# These will be used to generate the entry.tp file,
# and of course can also be used within this plugin's code.
# These could also live in a separate .py file which is then imported
# into your plugin's code, and be used directly to generate the entry.tp JSON.
#
# Some entries have default values (like "type" for a Setting),
# which are commented below and could technically be excluded from this code.
#
# Note that you may add any arbitrary keys/data to these dictionaries
# w/out breaking the generation routine. Only known TP SDK attributes
# (targeting the specified SDK version) will be used in the final entry.tp JSON.
##

# Basic plugin metadata
TP_PLUGIN_INFO = {
    'sdk': 3,
    'version': int(float(__version__) * 100),  # TP only recognizes integer version numbers
    'name': "Touch Portal Plugin Example",
    'id': PLUGIN_ID,
    "plugin_start_cmd": "%TP_PLUGIN_FOLDER%TPExamplePlugin\\pluginexample.exe",
    'configuration': {
        'colorDark': "#25274c",
        'colorLight': "#707ab5"
    }
}

# Setting(s) for this plugin. These could be either for users to
# set, or to persist data between plugin runs (as read-only settings).
TP_PLUGIN_SETTINGS = {
    'example': {
        'name': "Example Setting",
        # "text" is the default type and could be omitted here
        'type': "text",
        'default': "Example value",
        'readOnly': False,  # this is also the default
        'value': None  # we can optionally use the settings struct to hold the current value
    },
}

# This example only uses one Category for actions/etc., but multiple categories are supported also.
TP_PLUGIN_CATEGORIES = {
    "main": {
        'id': PLUGIN_ID + ".main",
        'name' : "Python Examples",
        # 'imagepath' : "icon-24.png"
    }
}

# Action(s) which this plugin supports.
TP_PLUGIN_ACTIONS = {
    'example': {
        # 'category' is optional, if omitted then this action will be added to all, or the only, category(ies)
        'category': "main",
        'id': PLUGIN_ID + ".act.example",
        'name': "Set Example State",
        'prefix': TP_PLUGIN_CATEGORIES['main']['name'],
        'type': "communicate",
        'tryInline': True,
        # 'format' tokens like $[1] will be replaced in the generated JSON with the corresponding data id wrapped with "{$...$}".
        # Numeric token values correspond to the order in which the data items are listed here, while text tokens correspond
        # to the last part of a dotted data ID (the part after the last period; letters, numbers, and underscore allowed).
        'format': "Set Example State Text to $[text] and Color to $[2]",
        'data': {
            'text': {
                'id': PLUGIN_ID + ".act.example.data.text",
                # "text" is the default type and could be omitted here
                'type': "text",
                'label': "Text",
                'default': "Hello World!"
            },
            'color': {
                'id': PLUGIN_ID + ".act.example.data.color",
                'type': "color",
                'label': "Color",
                'default': "#818181FF"
            },
        }
    },
}

# Plugin static state(s). These are listed in the entry.tp file,
# vs. dynamic states which would be created/removed at runtime.
TP_PLUGIN_STATES = {
    'text': {
        # 'category' is optional, if omitted then this state will be added to all, or the only, category(ies)
        'category': "main",
        'id': PLUGIN_ID + ".state.text",
        # "text" is the default type and could be omitted here
        'type': "text",
        'desc': "Example State Text",
        # we can conveniently use a value here which we already defined above
        'default': TP_PLUGIN_ACTIONS['example']['data']['text']['default']
    },
    'color': {
        'id': PLUGIN_ID + ".state.color",
        'desc': "Example State Color",
        'default': TP_PLUGIN_ACTIONS['example']['data']['color']['default']
    },
}

# Plugin Event(s).
TP_PLUGIN_EVENTS = {}

##
## End Python SDK declarations


# Create the Touch Portal API client.
try:
    TPClient = TP.Client(
        pluginId = PLUGIN_ID,  # required ID of this plugin
        sleepPeriod = 0.05,    # allow more time than default for other processes
        autoClose = True,      # automatically disconnect when TP sends "closePlugin" message
        checkPluginId = True,  # validate destination of messages sent to this plugin
        maxWorkers = 4,        # run up to 4 event handler threads
        updateStatesOnBroadcast = False,  # do not spam TP with state updates on every page change
    )
except Exception as e:
    sys.exit(f"Could not create TP Client, exiting. Error was:\n{repr(e)}")

# Crate the (optional) global logger
g_log = getLogger()

# Settings will be sent by TP upon initial connection to the plugin,
# as well as whenever they change at runtime. This example uses a
# shared function to handle both cases. See also onConnect() and onSettingUpdate()
def handleSettings(settings, on_connect=False):
    # the settings array from TP can just be flattened to a single dict,
    # from:
    #   [ {"Setting 1" : "value"}, {"Setting 2" : "value"} ]
    # to:
    #   { "Setting 1" : "value", "Setting 2" : "value" }
    settings = { list(settings[i])[0] : list(settings[i].values())[0] for i in range(len(settings)) }
    # now we can just get settings, and their values, by name
    if (value := settings.get(TP_PLUGIN_SETTINGS['example']['name'])) is not None:
        # this example doesn't do anything useful with the setting, just saves it
        TP_PLUGIN_SETTINGS['example']['value'] = value


## TP Client event handler callbacks

# Initial connection handler
@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    g_log.info(f"Connected to TP v{data.get('tpVersionString', '?')}, plugin v{data.get('pluginVersion', '?')}.")
    g_log.debug(f"Connection: {data}")
    if settings := data.get('settings'):
        handleSettings(settings, True)

# Settings handler
@TPClient.on(TP.TYPES.onSettingUpdate)
def onSettingUpdate(data):
    g_log.debug(f"Settings: {data}")
    if (settings := data.get('values')):
        handleSettings(settings, False)

# Action handler
@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    g_log.debug(f"Action: {data}")
    # check that `data` and `actionId` members exist and save them for later use
    if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
        return
    if aid == TP_PLUGIN_ACTIONS['example']['id']:
        # set our example State text and color values with the data from this action
        text = TPClient.getActionDataValue(action_data, TP_PLUGIN_ACTIONS['example']['data']['text'])
        color = TPClient.getActionDataValue(action_data, TP_PLUGIN_ACTIONS['example']['data']['color'])
        TPClient.stateUpdate(TP_PLUGIN_STATES['text']['id'], text)
        TPClient.stateUpdate(TP_PLUGIN_STATES['color']['id'], color)
    else:
        g_log.warning("Got unknown action ID: " + aid)

# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    g_log.info('Received shutdown event from TP Client.')
    # We do not need to disconnect manually because we used `autoClose = True`
    # when constructing TPClient()
    # TPClient.disconnect()

# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    g_log.error(f'Error in TP Client event handler: {repr(exc)}')
    # ... do something ?

## main

def main():
    global TPClient, g_log
    ret = 0  # sys.exit() value

    # handle CLI arguments
    parser = ArgumentParser()
    parser.add_argument("-d", action='store_true',
                        help="Use debug logging.")
    parser.add_argument("-w", action='store_true',
                        help="Only log warnings and errors.")
    parser.add_argument("-q", action='store_true',
                        help="Disable all logging (quiet).")
    parser.add_argument("-l", metavar="<logfile>",
                        help="Log to this file (default is stdout).")
    parser.add_argument("-s", action='store_true',
                        help="If logging to file, also output to stdout.")

    opts = parser.parse_args()
    del parser

    # set up logging
    if opts.q:
        # no logging at all
        g_log.addHandler(NullHandler())
    else:
        # set up pretty log formatting (similar to TP format)
        fmt = Formatter(
            fmt="{asctime:s}.{msecs:03.0f} [{levelname:.1s}] [{filename:s}:{lineno:d}] {message:s}",
            datefmt="%H:%M:%S", style="{"
        )
        # set the logging level
        if   opts.d: g_log.setLevel(DEBUG)
        elif opts.w: g_log.setLevel(WARNING)
        else:        g_log.setLevel(INFO)
        # set up log destination (file/stdout)
        if opts.l:
            try:
                # note that this will keep appending to any existing log file
                fh = FileHandler(str(opts.l))
                fh.setFormatter(fmt)
                g_log.addHandler(fh)
            except Exception as e:
                opts.s = True
                print(f"Error while creating file logger, falling back to stdout. {repr(e)}")
        if not opts.l or opts.s:
            sh = StreamHandler(sys.stdout)
            sh.setFormatter(fmt)
            g_log.addHandler(sh)

    # ready to go
    g_log.info(f"Starting {TP_PLUGIN_INFO['name']} v{__version__} on {sys.platform}.")

    try:
        # Connect to Touch Portal desktop application.
        # If connection succeeds, this method will not return (blocks) until the client is disconnected.
        TPClient.connect()
        g_log.info('TP Client closed.')
    except KeyboardInterrupt:
        g_log.warning("Caught keyboard interrupt, exiting.")
    except Exception:
        # This will catch and report any critical exceptions in the base TPClient code,
        # _not_ exceptions in this plugin's event handlers (use onError(), above, for that).
        from traceback import format_exc
        g_log.error(f"Exception in TP Client:\n{format_exc()}")
        ret = -1
    finally:
        # Make sure TP Client is stopped, this will do nothing if it is already disconnected.
        TPClient.disconnect()

    # TP disconnected, clean up.
    del TPClient

    g_log.info(f"{TP_PLUGIN_INFO['name']} stopped.")
    return ret


if __name__ == "__main__":
    sys.exit(main())
