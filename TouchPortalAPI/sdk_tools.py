#!/usr/bin/env python3
'''
Touch Portal Python SDK Tools

Functions:
	* Generates an entry.tp file for a Touch Portal plugin based
	on variables specified in the plugin source code (`generateEntryFromScript()`)
	or specified by value (`generateEntryFromDeclaration()`).
	* Validate an entry.tp attribute value against the minimum
	SDK version, value type, value content, etc. (`validateAttribValue()`).
	* ... ?


TODO/Ideas:

* Validate that IDs for states/actions/etc are unique.
# Dynamic default values, eg. for action prefix or category id/name (see notes in sdk_spec tables).
* Allow plugin author to set their own defaults?
* Automatic id substitution in action `format` attributes using placeholders.
'''

import sys
import os.path
import importlib.util
import json
# from argparse import ArgumentParser

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from sdk_spec import *

# globals
g_messages = []

def getMessages():
	return g_messages

def _addMessage(msg):
	global g_messages
	g_messages.append(msg)

def _clearMessages():
	global g_messages
	g_messages.clear()


def validateAttribValue(key, value, attrib_data, sdk_v):
	"""
	`key` is the attribute name;
	`value` is what to validate;
	`action_data` is the lookup table data for the given key (eg. `TPSDK_ATTRIBS_INFO[key]` );
	`sdk_v` is the TP SDK version being used (for validation).
	"""
	if value is None:
		if attrib_data.get('r'):
			_addMessage(f"WARNING: Missing required attribute '{key}'!")
		return False
	if not isinstance(value, (exp_typ := attrib_data.get('t', str))):
		_addMessage(f"WARNING: Wrong data type for attribute '{key}'! Expected {exp_typ} but got {type(value)}")
		return False
	if sdk_v < (min_sdk := attrib_data.get('v', sdk_v)):
		_addMessage(f"WARNING: Wrong SDK version for attribute '{key}'! Minimum is v{min_sdk} but using v{sdk_v}")
		return False
	if (choices := attrib_data.get('c')) and value not in choices:
		_addMessage(f"WARNING: Value error for attribute '{key}'! Got '{value}' but expected one of {choices}")
		return False
	return True


def dictFromItem(item, table, sdk_v = TPSDK_DEFAULT_VERSION):
	ret = {}
	for k, data in table.items():
		# try get explicit value from item
		if (v := item.get(k)) is None:
			# try get default value
			v = data.get('d')
		# check if there is nested data, eg. in an Action
		if isinstance(v, dict) and data.get('t') is list:
			v = arrayFromDict(v, data.get('l', {}), sdk_v)
		if validateAttribValue(k, v, data, sdk_v):
			ret[k] = v
	return ret


def arrayFromDict(d, table, sdk_v = TPSDK_DEFAULT_VERSION, category=None):
	ret = []
	for item in d.values():
		if not category or not (cat := item.get('category')) or cat == category:
			ret.append(dictFromItem(item, table, sdk_v))
	return ret


def getPluginVar(plugin, vname):
	return getattr(plugin, vname, {})


def generateEntryFromScript(script_path):
	"""
	Returns an "entry.tp" Python `dict` which is suitable for direct conversion to JSON format.
	`script_path` should be a valid python script file which contains "SDK declaration variables" like
	`TP_PLUGIN_INFO`, `TP_PLUGIN_SETTINGS`, etc. Note that the script is interpreted, so any actual
	"business" logic (like connecting to TP) should be in "__main__".
	May raise an `ImportError` if the plugin script could not be loaded or is missing required variables.
	Use `getMessages()` to check for any warnings/etc which may be generated (eg. from attribute validation).
	"""
	_clearMessages()
	# try to load the plugin script (business logic *must be* in __main__)
	try:
		# plugin = importlib.import_module(script_path)
		spec = importlib.util.spec_from_file_location("plugin", script_path)
		plugin = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(plugin)
		# print(plugin.TP_PLUGIN_INFO)
	except Exception as e:
		raise ImportError(f"ERROR while trying to import plugin code from '{script_path}': {repr(e)}")

	# Load the "standard SDK declaration variables" from plugin script into local scope
	# INFO and CATEGORY are required, rest are optional.
	info = getPluginVar(plugin, "TP_PLUGIN_INFO")
	if not info:
		raise ImportError(f"ERROR: Could not import required TP_PLUGIN_INFO variable from plugin source.")

	cats = getPluginVar(plugin, "TP_PLUGIN_CATEGORIES")
	if not cats:
		raise ImportError(f"ERROR: Could not import required TP_PLUGIN_CATEGORIES variable from plugin source.")

	return generateEntryFromDeclaration(
		info, cats,
		settings=getPluginVar(plugin, "TP_PLUGIN_SETTINGS"),
		actions=getPluginVar(plugin, "TP_PLUGIN_ACTIONS"),
		states=getPluginVar(plugin, "TP_PLUGIN_STATES"),
		events=getPluginVar(plugin, "TP_PLUGIN_EVENTS"),
		connectors=getPluginVar(plugin, "TP_PLUGIN_CONNECTORS")
	)


def generateEntryFromDeclaration(info:dict, categories:dict, **kwargs):
	"""
	Returns an "entry.tp" Python `dict` which is suitable for direct conversion to JSON format.
	Arguments should contain SDK declaration dict values, for example as specified for `TP_PLUGIN_INFO`,
	etc.  The `info` and `category` values are required, the rest are optional.
	Use `getMessages()` to check for any warnings/etc which may be generated (eg. from attribute validation).
	`kwargs` can be one or more of:
		settings:dict={},
		actions:dict={},
		states:dict={},
		events:dict={},
		connectors:dict={}
	"""
	settings = kwargs.get('settings', {})
	actions = kwargs.get('actions', {})
	states = kwargs.get('states', {})
	events = kwargs.get('events', {})
	connectors = kwargs.get('connectors', {})
	# print(info, categories, settings, actions, states, events, connectors)

	# Start the root entry.tp object using basic plugin metadata
	# This will also create an empty `categories` array in the root of the entry.
	entry = dictFromItem(info, TPSDK_ATTRIBS_ROOT)

	# Get the target SDK version (was either specified in plugin or is TPSDK_DEFAULT_VERSION)
	tgt_sdk_v = entry['sdk']

	# Loop over each plugin category and set up actions, states, events, and connectors.
	for cat, data in categories.items():
		category = dictFromItem(data, TPSDK_ATTRIBS_CATEGORY, tgt_sdk_v)
		category['actions'] = arrayFromDict(actions, TPSDK_ATTRIBS_ACTION, tgt_sdk_v, cat)
		category['states'] = arrayFromDict(states, TPSDK_ATTRIBS_STATE, tgt_sdk_v, cat)
		category['events'] = arrayFromDict(events, TPSDK_ATTRIBS_EVENT, tgt_sdk_v, cat)
		if tgt_sdk_v >= 4:
			category['connectors'] = arrayFromDict(connectors, TPSDK_ATTRIBS_CONNECTOR, tgt_sdk_v, cat)
		# add the category to entry's categories array
		entry['categories'].append(category)

	# Add Settings to root
	if tgt_sdk_v >= 3:
		entry['settings'] = arrayFromDict(settings, TPSDK_ATTRIBS_SETTINGS, tgt_sdk_v)

	return entry


## main

# for now main() just runs the entry.tp generator routine, but this could be controlled with CLI arguments
def main():
	# Get the plugin script name from command line (default is "main.py")
	script_path = sys.argv[1] if len(sys.argv) > 1 else "main.py"
	# if script_path.endswith(".py"):
	# 	script_path = script_path.rsplit(".", 1)[0]
	if len(script_path.split(".")) < 2:
		script_path = script_path + ".py"

	# define the output file (TODO: make output path/device an option)
	entry_path = "./entry.tp"

	print("")
	print(f"Generating '{entry_path}' from {script_path} \n")

	try:
		entry = generateEntryFromScript(script_path)
	except Exception as e:
		return str(e)

	if (messages := getMessages()):
		print(messages)
		print("")

	# see what we got
	print(json.dumps(entry, indent=2))
	print("")

	# write it to a file
	try:
		with open(entry_path, "w") as entry_file:
			entry_file.write(json.dumps(entry, indent=2))
	except Exception as e:
		return f"ERROR while trying to write to '{entry_path}': {repr(e)}"

	print(f"Finished writing {entry_path}\n")
	return 0

if __name__ == "__main__":
	sys.exit(main())
