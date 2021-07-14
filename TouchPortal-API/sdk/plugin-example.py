#!/usr/bin/env python3
'''
Touch Portal Plugin Example
'''

import sys

# load the TP Python API
# FIXME awkward import because of sibling folder structure
import os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
import TouchPortalAPI as TP

# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)


# Version string of this plugin (in Python style).
__version__ = "1.0"
# The unique plugin ID string is used in multiple places.
PLUGIN_ID = "tp.plugin.example.python"

## Start Python SDK declarations
# These will be used to generate the entry.tp file,
# and of course can also be used within this plugin's code.

# Basic plugin metadata
TP_PLUGIN_INFO = {
	'sdk': 3,
	'version': int(float(__version__) * 100),  # TP only recognizes integer version numbers
	'name': "Touch Portal Plugin Example",
	'id': PLUGIN_ID,
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
		'type': "text",
		'default': "Example value",
		'readOnly': False,
		'value': None  # we can optionally use the settings struct to hold the current value
	},
}

# This example only uses one Category for actions/etc., but multiple categories are supported also.
TP_PLUGIN_CATEGORIES = {
	"main": {
		'id': PLUGIN_ID + ".Main",
		'name' : "Python Examples",
		'imagepath' : "icon-24.png"
	}
}

# Action(s) which this plugin supports.
TP_PLUGIN_ACTIONS = {
	'example': {
		'category': "main",  # this is optional, if omitted then action will be added to all categories
		'id': PLUGIN_ID + ".act.example",
		'name': "Set Example State",
		'prefix': TP_PLUGIN_CATEGORIES['main']['name'],
		'type': "communicate",
		'format': "Set Example State text to {$" + PLUGIN_ID + ".act.example.data$}",
		'data': {
			'example_data': {
				'id': PLUGIN_ID + ".act.example.data",
				'type': "text",
				'label': "Text",
				'default': "Hello World!"
			},
		}
	},
}

# Plugin static state(s). These are listed in the entry.tp file,
# vs. dynamic states which would be created/removed at runtime.
TP_PLUGIN_STATES = {
	'example': {
		# 'category': "main",  # this is optional, if omitted then state will be added to all categories
		'id': PLUGIN_ID + ".state.example",
		'type': "text",
		'desc': "Example State",
		'default': "Set me!"
	},
}

# Plugin Event(s).
TP_PLUGIN_EVENTS = {}

## End Python SDK declarations


# Create the Touch Portal API client.
try:
	TPClient = TP.Client(
		pluginId = PLUGIN_ID,  # required ID of this plugin
		sleepPeriod = 0.05,    # allow more time than default for other processes
		autoClose = True,      # automatically disconnect when TP sends "closePlugin" message
		checkPluginId = True,  # validate destincation of messages sent to this plugin
		maxWorkers = 4         # run up to 4 event handler threads
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
		# set our example State value with the data from this action
		text = TP.getActionDataValue(action_data, TP_PLUGIN_ACTIONS['example']['data']['example_data'])
		TPClient.stateUpdate(TP_PLUGIN_STATES['example']['id'], text)
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
		g_log.addHandler(NullHandler())
	else:
		fmt = Formatter(
			fmt="{asctime:s}.{msecs:03.0f} [{levelname:.1s}] [{filename:s}:{lineno:d}] {message:s}",
			datefmt="%H:%M:%S", style="{"
		)
		if opts.d:
			g_log.setLevel(DEBUG)
		elif opts.w:
			g_log.setLevel(WARNING)
		else:
			g_log.setLevel(INFO)
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
		# _not_ excpetions in this plugin's event handlers (use onError(), above, for that).
		from traceback import format_exc
		g_log.error(f"Exception in TP Client:\n{format_exc()}")
		ret = -1
	finally:
		TPClient.disconnect()  # make sure it's stopped, no-op if already stopped.

	# TP disconnected, clean up.
	del TPClient

	g_log.info(f"{TP_PLUGIN_INFO['name']} stopped.")
	return ret


if __name__ == "__main__":
	sys.exit(main())
