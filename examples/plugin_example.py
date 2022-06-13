"""
Touch Portal Plugin Example
"""

import sys

# Load the TP Python API. Note that TouchPortalAPI must be installed (eg. with pip)
# _or_ be in a folder directly below this plugin file.
import TouchPortalAPI as TP

# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from TouchPortalAPI.logger import Logger


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
    # Startup command, with default logging options read from configuration file (see main() for details)
    "plugin_start_cmd": "%TP_PLUGIN_FOLDER%TPExamplePlugin\\pluginexample.exe @plugin-example-conf.txt",
    'configuration': {
        'colorDark': "#25274c",
        'colorLight': "#707ab5"
    },
    'doc': {
        "description": "This is an example plugin for Touch Portal. It demonstrates the basics of how to create a plugin, and how to communicate with Touch Portal.",
        "repository": "KillerBOSS2019:TP-YTDM-Plugin",
        "Install": "1. Download .tpp file\n2. in TouchPortal gui click gear icon and select 'Import Plugin'\n3. Select the .tpp file\n4. Click 'Import'",
    }
}

# Setting(s) for this plugin. These could be either for users to
# set, or to persist data between plugin runs (as read-only settings).
TP_PLUGIN_SETTINGS = {
    'example': {
        'doc': "Example setting doc", # testing purposes
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
        "doc": "This action sets the example setting to a given value, and also sets the color of the example setting to a given value.",
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
    'Inc/DecrVol': {
        # 'category' is optional, if omitted then this action will be added to all, or the only, category(ies)
        'category': "main",
        'id': PLUGIN_ID + ".act.Inc/DecrVol",
        'name': 'Volume Mixer: Increase/Decrease process volume',
        'prefix': TP_PLUGIN_CATEGORIES['main']['name'],
        'type': "communicate",
        'tryInline': True,
        'format': "$[2]$[1]Volume to$[3]",
        "doc": "This action increases or decreases the process volume of the selected process.",
        "hasHoldFunctionality": True,
        'data': {
            'AppChoice': {
                'id': PLUGIN_ID + ".act.Inc/DecrVol.data.process",
                # "text" is the default type and could be omitted here
                'type': "choice",
                'label': "process list",
                'default': "",
                "valueChoices": []
                
            },
            'OptionList': {
                'id': PLUGIN_ID + ".act.Inc/DecrVol.data.choice",
                'type': "choice",
                'label': "Option choice",
                'default': "Increase",
                "valueChoices": [
                    "Increase",
                    "Decrease",
                    "Set"
                ]
            },
            'Volume': {
                'id': PLUGIN_ID + ".act.Inc/DecrVol.data.Volume",
                'type': "number",
                'label': "Volume",
                "allowDecimals": False,
                "minValue": 0,
                "maxValue": 100,
                "default": 10
            },
        }
    },
     'AppMute': {
        # 'category' is optional, if omitted then this action will be added to all, or the only, category(ies)
        'category': "main",
        'id': PLUGIN_ID + ".act.Mute/Unmute",
        'name': 'Volume Mixer: Mute/Unmute process volume',
        'prefix': TP_PLUGIN_CATEGORIES['main']['name'],
        'type': "communicate",
        'tryInline': True,
        # 'format' tokens like $[1] will be replaced in the generated JSON with the corresponding data id wrapped with "{$...$}".
        # Numeric token values correspond to the order in which the data items are listed here, while text tokens correspond
        # to the last part of a dotted data ID (the part after the last period; letters, numbers, and underscore allowed).
        'format': "$[2] Program:$[1]",
        "hasHoldFunctionality": True,
        "doc": "This action mutes or unmutes the selected process.",
        'data': {
            'appChoice': {
                'id': PLUGIN_ID + ".act.Mute/Unmute.data.process",
                # "text" is the default type and could be omitted here
                'type': "choice",
                'label': "process list",
                'default': "",
                "valueChoices": []
                
            },
            'OptionList': {
                'id': PLUGIN_ID + ".act.Mute/Unmute.data.choice",
                'type': "choice",
                'label': "Option choice",
                'default': "Toggle",
                "valueChoices": [
                    "Mute",
                    "Unmute",
                    "Toggle"
                ]
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
# TPClient: TP.Client = None  # instance of the TouchPortalAPI Client, created in main()

# Crate the (optional) global logger, an instance of `TouchPortalAPI::Logger` helper class.
# Logging configuration is set up in main().
g_log = Logger(name = PLUGIN_ID)

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

    # default log file destination
    logFile = f"./{PLUGIN_ID}.log"
    # default log stream destination
    logStream = sys.stdout

    # Set up and handle CLI arguments. These all relate to logging options.
    # The plugin can be run with "-h" option to show available argument options.
    # Addtionally, a file constaining any of these arguments can be specified on the command line
    # with the `@` prefix. For example: `plugin-example.py @config.txt`
    # The file must contain one valid argument per line, including the `-` or `--` prefixes.
    # See the plugin-example-conf.txt file for an example config file.
    parser = ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("-d", action='store_true',
                        help="Use debug logging.")
    parser.add_argument("-w", action='store_true',
                        help="Only log warnings and errors.")
    parser.add_argument("-q", action='store_true',
                        help="Disable all logging (quiet).")
    parser.add_argument("-l", metavar="<logfile>",
                        help=f"Log file name (default is '{logFile}'). Use 'none' to disable file logging.")
    parser.add_argument("-s", metavar="<stream>",
                        help="Log to output stream: 'stdout' (default), 'stderr', or 'none'.")

    # his processes the actual command line and populates the `opts` dict.
    opts = parser.parse_args()
    del parser

    # trim option string (they may contain spaces if read from config file)
    opts.l = opts.l.strip()
    opts.s = opts.s.strip().lower()
    print(opts)

    # Set minimum logging level based on passed arguments
    logLevel = "INFO"
    if opts.q: logLevel = None
    elif opts.d: logLevel = "DEBUG"
    elif opts.w: logLevel = "WARNING"

    # set log file if -l argument was passed
    if opts.l:
        logFile = None if opts.l.lower() == "none" else opts.l
    # set console logging if -s argument was passed
    if opts.s:
        if opts.S == "stderr": logStream = sys.stderr
        elif opts.s == "stdout": logStream = sys.stdout
        else: logStream = None

    # Configure the Client logging based on command line arguments.
    # Since the Client uses the "root" logger by default,
    # this also sets all default logging options for any added child loggers, such as our g_log instance we created earlier.
    TPClient.setLogFile(logFile)
    TPClient.setLogStream(logStream)
    TPClient.setLogLevel(logLevel)

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
