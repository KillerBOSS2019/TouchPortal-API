#!/usr/bin/env python3
'''
Touch Portal Python SDK Tools

Functions:
	* Generates an entry.tp definition file for a Touch Portal plugin based
	on variables specified in the plugin source code (`generateDefinitionFromScript()`)
	or specified by value (`generateDefinitionFromDeclaration()`).
	* Validate an entire plugin definition (entry.tp) file (`validateDefinitionFile()`),
	string (`validateDefinitionString()`), or object (`validateDefinitionObject()`).
	* Validate an entry.tp attribute value against the minimum
	SDK version, value type, value content, etc. (`validateAttribValue()`).
	* ... ?

Command-line Usage:
	sdk_tools.py [-h] [action] [target] [output]

	* `action` : "--generate" (default) to generate definition file or "--validate" to validate definition file.
	* `target` : path to file, type depending on action.
	           Either a plugin script for `generate` or an entry.tp file for `validate`. Paths are relative to current
						 working directory. Defaults to "./main.py" and "./entry.tp" respectively.
	* `output` : optional output file path for generated definition JSON, or "stdout" to print to console.

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

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from sdk_spec import *

## globals
g_messages = []

## Utils

def getMessages():
	return g_messages

def printMessages(message_array):
	for msg in message_array:
		print(msg)

def _addMessage(msg):
	global g_messages
	g_messages.append(msg)

def _clearMessages():
	global g_messages
	g_messages.clear()

def _normPath(path):
	return os.path.normpath(os.path.join(os.getcwd(), path))


## Generator functions

def _dictFromItem(item, table, sdk_v = TPSDK_DEFAULT_VERSION):
	ret = {}
	for k, data in table.items():
		# try get explicit value from item
		if (v := item.get(k)) is None:
			# try get default value
			v = data.get('d')
		# check if there is nested data, eg. in an Action
		if isinstance(v, dict) and data.get('t') is list:
			v = _arrayFromDict(v, data.get('l', {}), sdk_v)
		if validateAttribValue(k, v, data, sdk_v):
			ret[k] = v
	return ret


def _arrayFromDict(d, table, sdk_v = TPSDK_DEFAULT_VERSION, category=None):
	ret = []
	for item in d.values():
		if not category or not (cat := item.get('category')) or cat == category:
			ret.append(_dictFromItem(item, table, sdk_v))
	return ret


def _getPluginVar(plugin, vname):
	return getattr(plugin, vname, {})


def generateDefinitionFromScript(script_path):
	"""
	Returns an "entry.tp" Python `dict` which is suitable for direct conversion to JSON format.
	`script_path` should be a valid python script file which contains "SDK declaration variables" like
	`TP_PLUGIN_INFO`, `TP_PLUGIN_SETTINGS`, etc. Note that the script is interpreted, so any actual
	"business" logic (like connecting to TP) should be in "__main__".
	May raise an `ImportError` if the plugin script could not be loaded or is missing required variables.
	Use `getMessages()` to check for any warnings/etc which may be generated (eg. from attribute validation).
	"""
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
	info = _getPluginVar(plugin, "TP_PLUGIN_INFO")
	if not info:
		raise ImportError(f"ERROR: Could not import required TP_PLUGIN_INFO variable from plugin source.")

	cats = _getPluginVar(plugin, "TP_PLUGIN_CATEGORIES")
	if not cats:
		raise ImportError(f"ERROR: Could not import required TP_PLUGIN_CATEGORIES variable from plugin source.")

	return generateDefinitionFromDeclaration(
		info, cats,
		settings=_getPluginVar(plugin, "TP_PLUGIN_SETTINGS"),
		actions=_getPluginVar(plugin, "TP_PLUGIN_ACTIONS"),
		states=_getPluginVar(plugin, "TP_PLUGIN_STATES"),
		events=_getPluginVar(plugin, "TP_PLUGIN_EVENTS"),
		connectors=_getPluginVar(plugin, "TP_PLUGIN_CONNECTORS")
	)


def generateDefinitionFromDeclaration(info:dict, categories:dict, **kwargs):
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
	_clearMessages()
	settings = kwargs.get('settings', {})
	actions = kwargs.get('actions', {})
	states = kwargs.get('states', {})
	events = kwargs.get('events', {})
	connectors = kwargs.get('connectors', {})
	# print(info, categories, settings, actions, states, events, connectors)

	# Start the root entry.tp object using basic plugin metadata
	# This will also create an empty `categories` array in the root of the entry.
	entry = _dictFromItem(info, TPSDK_ATTRIBS_ROOT)

	# Get the target SDK version (was either specified in plugin or is TPSDK_DEFAULT_VERSION)
	tgt_sdk_v = entry['sdk']

	# Loop over each plugin category and set up actions, states, events, and connectors.
	for cat, data in categories.items():
		category = _dictFromItem(data, TPSDK_ATTRIBS_CATEGORY, tgt_sdk_v)
		category['actions'] = _arrayFromDict(actions, TPSDK_ATTRIBS_ACTION, tgt_sdk_v, cat)
		category['states'] = _arrayFromDict(states, TPSDK_ATTRIBS_STATE, tgt_sdk_v, cat)
		category['events'] = _arrayFromDict(events, TPSDK_ATTRIBS_EVENT, tgt_sdk_v, cat)
		if tgt_sdk_v >= 4:
			category['connectors'] = _arrayFromDict(connectors, TPSDK_ATTRIBS_CONNECTOR, tgt_sdk_v, cat)
		# add the category to entry's categories array
		entry['categories'].append(category)

	# Add Settings to root
	if tgt_sdk_v >= 3:
		entry['settings'] = _arrayFromDict(settings, TPSDK_ATTRIBS_SETTINGS, tgt_sdk_v)

	return entry


## Validation functions

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

def _validateDefinitionDict(d, table, sdk_v):
	# iterate over existing attributes to validate them
	for k, v in d.items():
		adata = table.get(k)
		if not adata:
			_addMessage(f"WARNING: Attribute '{k}' is unknown.")
			continue
		if not validateAttribValue(k, v, adata, sdk_v):
			continue
		# print(k, v, type(v))
		if isinstance(v, list) and (ltable := adata.get('l')):
			_validateDefinitionArray(v, ltable, sdk_v)
	# iterate over table entries to check if all required attribs are present
	for k, data in table.items():
		if data.get('r') and k not in d.keys():
			_addMessage(f"WARNING: Missing required attribute '{k}'.")

def _validateDefinitionArray(a, table, sdk_v):
	for item in a:
		if isinstance(item, dict):
			_validateDefinitionDict(item, table, sdk_v)
		else:
			_addMessage(f"WARNING: Unable to handle array member '{item}'.")


def validateDefinitionObject(data):
	"""
	Validates a TP plugin definition structure from a Python `dict` object.
	`data` is a de-serialzed entry.tp JSON object (eg. json.load('entry.tp'))
	Returns `True` if no problems were found, `False` otherwise.
	Use `getMessages()` to check for any validation warnings which may be generated.
	"""
	_clearMessages()
	sdk_v = data.get('sdk', TPSDK_DEFAULT_VERSION)
	_validateDefinitionDict(data, TPSDK_ATTRIBS_ROOT, sdk_v)
	return len(g_messages) == 0

def validateDefinitionString(data):
	"""
	Validates a TP plugin definition structure from JSON string.
	`data` is an entry.tp JSON string
	Returns `True` if no problems were found, `False` otherwise.
	Use `getMessages()` to check for any validation warnings which may be generated.
	"""
	return validateDefinitionObject(json.loads(data))

def validateDefinitionFile(file_path):
	"""
	Validates a TP plugin definition structure from JSON file.
	`file_path` is a valid system path to an entry.tp JSON file
	Returns `True` if no problems were found, `False` otherwise.
	Use `getMessages()` to check for any validation warnings which may be generated.
	"""
	with open(file_path, 'r') as tpfile:
		return validateDefinitionObject(json.load(tpfile))


## CLI handlers

def _generateDefinition(script_path, output_path):
	if len(script_path.split(".")) < 2:
		script_path = script_path + ".py"

	print(f"Generating plugin definition JSON from {script_path} \n")
	entry = generateDefinitionFromScript(script_path)
	if (messages := getMessages()):
		printMessages(messages)
		print("")
	# output
	if output_path:
		# write it to a file
		with open(output_path, "w") as entry_file:
			entry_file.write(json.dumps(entry, indent=2))
			print(f"Saved generated JSON to {output_path}\n")
	else:
		# see what we got
		print(json.dumps(entry, indent=2))
		print("")
	print(f"Finished generating plugin definition JSON.\n")


def _validateDefinition(entry_path):
	print(f"Validating {entry_path}, any errors or warnings will be printed below.\n")
	if validateDefinitionFile(entry_path):
		print("No problems found!")
	else:
		printMessages(getMessages())
	print(f"\nFinished validating {entry_path}\n")


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("--generate", action='store_true',
	                    help="Generate a definition file from plugin script data. This is the default action.")
	parser.add_argument("--validate", action='store_true',
	                    help="Validate a definition JSON file (entry.tp). If given with `generate` then will validate the generated JSON output file.")
	parser.add_argument("-o", metavar="<file_path>",
	                    help="Output file for `generate` action. Default will be a file named 'entry.tp' in the same folder as the input script. "
											"Use 'stdout' to print the output to the console instead.")
	parser.add_argument("target", metavar="target", nargs="?", default="",
	                    help="Either a plugin script for `generate` or an entry.tp file for `validate`. "
	                         "Paths are relative to current working directory. Defaults to './main.py' and './entry.tp' respectively.")
	opts = parser.parse_args()
	del parser

	# default action
	opts.generate = opts.generate or not opts.validate

	print("")

	try:

		if opts.generate:
			opts.target = _normPath(opts.target or "main.py")
			output_path = None
			if opts.o:
				if opts.o != "stdout":
					output_path = opts.o
			else:
				output_path = os.path.join(os.path.dirname(opts.target), "entry.tp")
			_generateDefinition(opts.target, output_path)
			if opts.validate:
				if output_path:
					opts.target = output_path
				else:
					opts.validate = False  # output sent to stdout, nothing to validate

		if opts.validate:
			opts.target = _normPath(opts.target or "entry.tp")
			_validateDefinition(opts.target)

	except Exception as e:
		return str(e)

	return 0


if __name__ == "__main__":
	sys.exit(main())
