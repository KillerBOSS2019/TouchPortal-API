#!/usr/bin/env python3
'''
Generates an entry.tp file for a Touch Portal plugin based
on variables specified in the plugin source code.
'''

import sys
import importlib
import json
# from argparse import ArgumentParser

'''
TODO/Ideas:

* Validate required attribute keys/values (per target SDK version?)
* Allow for default values (eg. SDK version ).
* Allow plugin author to set their own defaults.
* Allow for multiple Categories

* Perhaps something like this for each main TP API Collection:

SDK_ATTRIBS_INFO = {
# key name             sdk V,  required,   default value (if any)
	'sdk':              {'v': 1, 'r': True, 'd': 4},
	'version':          {'v': 1, 'r': True, 'd': 1},
	'name':             {'v': 1, 'r': True},
	'id':               {'v': 1, 'r': True},
	'configuration':    {'v': 1, 'r': False},
	'plugin_start_cmd': {'v': 1, 'r': False}
}

'''

def dictFromItem(item, keys):
	ret = {}
	for k in keys:
		if (v := item.get(k)) != None:
			ret[k] = v
	return ret


def arrayFromDict(d, keys):
	ret = []
	for item in d.values():
		ret.append(dictFromItem(item, keys))
	return ret


def getPluginVar(plugin, vname, required=False):
	try:
		return getattr(plugin, vname)
	except:
		if required:
			sys.exit(f"ERROR: Could not import required {vname} variable from plugin source.")
		return {}

def main():
	# Get the plugin script name from command line (default is "main.py")
	pscript = sys.argv[1] if len(sys.argv) > 1 else "main.py"
	if pscript.endswith(".py"):
		pscript = pscript.rsplit(".", 1)[0]

	# define the output file (TODO: make output path/device an option)
	entry_path = "./entry.tp"

	# try to load the plugin script (business logic *must be* in __main__)
	try:
		plugin = importlib.import_module(pscript)
	except Exception as e:
		return f"ERROR while trying to import plugin code from '{pscript}': {repr(e)}"

	print("")
	print(f"Generating '{entry_path}' from {pscript}.py \n")

	# Load the "standard SDK declaration variables" from plugin script into local scope
	# INFO and CATEGORY are required, rest are optional.
	info = getPluginVar(plugin, "TP_PLUGIN_INFO", True)
	cat = getPluginVar(plugin, "TP_PLUGIN_CATEGORY", True)
	settings = getPluginVar(plugin, "TP_PLUGIN_SETTINGS")
	actions = getPluginVar(plugin, "TP_PLUGIN_ACTIONS")
	states = getPluginVar(plugin, "TP_PLUGIN_STATES")
	events = getPluginVar(plugin, "TP_PLUGIN_EVENTS")
	connectors = getPluginVar(plugin, "TP_PLUGIN_CONNECTORS")
	# print(info, cat, settings, actions, states, events)

	# Start the root entry.tp object using basic plugin metadata
	entry = dictFromItem(info, ['sdk', 'version', 'name', 'id', 'configuration', 'plugin_start_cmd'])
	# Add Settings to root
	entry['settings'] = arrayFromDict(settings, ['name', 'default', 'type', 'maxLength', 'isPassword', 'minValue', 'maxValue', 'readOnly'])

	# Now we add actions, states, events to the Category object

	# Actions are special because they contain nested data structs
	cat['actions'] = []
	for item in actions.values():
		act = {}
		for k, v in item.items():
			if k == "data":
				act[k] = arrayFromDict(v, ['id', 'type', 'label', 'default', 'valueChoices', 'extensions', 'allowDecimals', 'minValue', 'maxValue'])
			elif k in ('id', 'name', 'prefix', 'type', 'executionType', 'execution_cmd', 'description', 'tryInline', 'format', 'hasHoldFunctionality'):
				act[k] = v
		cat['actions'].append(act)

	cat['states'] = arrayFromDict(states, ['id', 'type', 'desc', 'default', 'valueChoices'])
	cat['events'] = arrayFromDict(events, ['id', 'name', 'format', 'type', 'valueChoices', 'valueType', 'valueStateId'])

	if entry['sdk'] > 3:
		# Connectors `data` member probably needs same treatment as Actions' `data` but TP API docs are still vague
		cat['connectors'] = arrayFromDict(connectors, ['id', 'name', 'format', 'data'])

	# And finally add the built category structure to the root entry.tp object.
	entry['categories'] = [cat]

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
