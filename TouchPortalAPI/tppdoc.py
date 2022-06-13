import sys, os
import importlib
from argparse import ArgumentParser

def getInfoFromBuildScript(script:str):
	try:
		sys.path.insert(1, os.getcwd()) # This allows build config to import stuff
		spec = importlib.util.spec_from_file_location("entry", script)
		entry = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(entry)
	except Exception as e:
		raise ImportError(f"ERROR while trying to import entry code from '{script}': {repr(e)}")
	return entry

def generateTableContent(entry, entryFile):
    table_content = f"""
# {entry['name'].replace(" ", "-")}

![Downloads](https://img.shields.io/github/downloads/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]}/total)
![Forks](https://img.shields.io/github/forks/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]})
![Stars](https://img.shields.io/github/stars/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]})
![License](https://img.shields.io/github/license/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]})
- [{entry['name']}](#{entry['name'].replace(" ", "-")})
  - [Description](#description)
    """

    if hasattr(entryFile, "TP_PLUGIN_SETTINGS") and entryFile.TP_PLUGIN_SETTINGS:
        table_content += """- [Settings Overview](#Settings-Overview)"""

    table_content += """
  - [Features](#Features)"""

    if "TP_PLUGIN_ACTIONS" in dir(entryFile) and entryFile.TP_PLUGIN_ACTIONS:
        table_content += """
    - [Actions](#actions)"""

    if "TP_PLUGIN_STATES" in dir(entryFile) and entryFile.TP_PLUGIN_STATES:
        table_content += """
    - [States](#states)"""

    if "TP_PLUGIN_EVENTS" in dir(entryFile) and entryFile.TP_PLUGIN_EVENTS:
        table_content += """
    - [Events](#events)"""

    if "Install" in entry['doc'].keys() and entry['doc']['Install']:
        table_content += """
  - [Installation Guide](#installation)"""
        
    table_content += """
  - [Bugs and Support](#Bugs-and-Suggestion)
  - [License](#license)
  """
    return table_content


def generateAction(entry):
    actionDoc = "\n## Actions\n"
    table = "<table>\n"

    table += "<tr valign='buttom'>" + "<th>Action Name</th>" + "<th>Description</th>" + "<th>Format</th>" + \
        "<th nowrap>Data<br/><div align=left><sub>choices/default (in bold)</th>" + \
        "<th>On<br/>Hold</sub></div></th>" + \
        "</tr>\n"

    for action in entry.keys():
        table += f"<tr valign='top'><td>{action}</td>" + \
            f"<td>{entry[action]['doc']}</td>" + \
            f"<td>{entry[action]['format'].replace('$', '')}</td>"

        table += "<td><ul start=0>\n"

        for data in entry[action]['data'].keys():
            table += f"<li>[{data}] Type: {entry[action]['data'][data]['type']} &nbsp; \n"

            if entry[action]['data'][data]['type'] == "choice" and entry[action]['data'][data]['valueChoices']:
                table += f"<b>{entry[action]['data'][data]['default']}</b> {entry[action]['data'][data]['valueChoices']}"
            elif "default" in entry[action]['data'][data].keys() and entry[action]['data'][data]['default'] != "":
                table += f"<b>{entry[action]['data'][data]['default']}</b>"
            else:
                table += "&lt;empty&gt;"

            if entry[action]['data'][data]['type'] == "number":
                table += f" ({entry[action]['data'][data]['minValue']}-{entry[action]['data'][data]['maxValue']})"
            table += "</li>\n"

        table += "</ul></td>\n"
        table += f"<td align=center>{'Yes' if 'hasHoldFunctionality' in entry[action]['data'][data].keys() and entry[action]['data'][data]['hasHoldFunctionality'] else 'No'}</td>\n"

    table += "</table>\n"

    actionDoc += table

    return actionDoc

def generateSetting(entry):
    settingDoc = "\n## Settings Overview\n"

    for setting in entry.keys():
        settingDoc += f"### {setting}\n"
        settingDoc += "| Read-only | Type | Default Value"
        if "maxLength" in entry[setting].keys() and entry[setting]['maxLength']:
            settings += f" | Max. Length"
        if "minValue" in entry[setting].keys() and entry[setting]['minValue']:
            settings += f" | Min. Value"
        if "maxValue" in entry[setting].keys() and entry[setting]['maxValue']:
            settings += f" | Max. Value"
        settingDoc += " |\n"
        settingDoc += "| --- | --- | ---"
        if "maxLength" in entry[setting].keys() and entry[setting]['maxLength']:
            settingDoc += f" | ---"
        if "minValue" in entry[setting].keys() and entry[setting]['minValue']:
            settingDoc += f" | ---"
        if "maxValue" in entry[setting].keys() and entry[setting]['maxValue']:
            settingDoc += f" | ---"

        settingDoc += " |\n"
        settingDoc += f"| {entry[setting]['readOnly']} | {entry[setting]['type']} | {entry[setting]['default']}"

        if "maxLength" in entry[setting].keys() and entry[setting]['maxLength']:
            settingDoc += f" | {entry[setting]['maxLength']}"
        if "minValue" in entry[setting].keys() and entry[setting]['minValue']:
            settingDoc += f" | {entry[setting]['minValue']}"
        if "maxValue" in entry[setting].keys() and entry[setting]['maxValue']:
            settingDoc += f" | {entry[setting]['maxValue']}"
        settingDoc += " |\n\n"
        settingDoc += f"{entry[setting]['doc']}\n\n"
    return settingDoc

def generateState(entry, baseid):
    stateDoc = "\n### States\n"

    stateDoc += f" <b>Base Id:</b> {baseid}.\n\n"
    stateDoc += "| Id | Name | Description | DefaultValue |\n"
    stateDoc += "| --- | --- | --- | --- |\n"
    for state in entry.keys():
        stateDoc += f"| {entry[state]['id'].split(baseid)[1]} | {state} | {entry[state]['desc']} | {entry[state]['default']} |\n"
    stateDoc += "\n\n"
    return stateDoc

def main(docArg=None):
    parser = ArgumentParser(description=
        "Script to automatically generates a documentation for a TouchPortal plugin.")

    parser.add_argument(
        "target", metavar='<target>', type=str,
        help='A build script that contains some infomations about the plugin. ' +
        'Using given infomation about the plugin, this script will automatically build entry.tp (if given file is .py) and it will build the distro ' +
        'based on which operating system you\'re using.'
    )

    opts = parser.parse_args(docArg)
    del parser

    out_dir = os.path.dirname(opts.target)

    if out_dir:
        os.chdir(out_dir)

    entry = getInfoFromBuildScript(os.path.basename(opts.target))

    documentation = """"""

    tableContent = generateTableContent(entry.TP_PLUGIN_INFO, entry)
    documentation += tableContent

    documentation += f"""

# Description
{entry.TP_PLUGIN_INFO['doc']['description']}
    """
    setting = generateSetting(entry.TP_PLUGIN_SETTINGS)
    documentation += setting

    documentation += "\n# Features\n"
    action = generateAction(entry.TP_PLUGIN_ACTIONS)
    documentation += action

    state = generateState(entry.TP_PLUGIN_STATES, entry.TP_PLUGIN_INFO['id'])
    documentation += state

    if entry.TP_PLUGIN_INFO['doc'].get('Install'):
        documentation += "\n# Installation\n"
        documentation += entry.TP_PLUGIN_INFO['doc']['Install']

    documentation += "\n# Bugs and Suggestion\n"
    documentation += f"Open an [issue](https://github.com/{'/'.join(entry.TP_PLUGIN_INFO['doc']['repository'].split(':'))}/issues) or join offical [TouchPortal Discord](https://discord.gg/MgxQb8r) for support.\n\n"

    documentation += "\n# License\n"
    documentation += "This plugin is licensed under the [GPL 3.0 License] - see the [LICENSE](LICENSE) file for more information.\n\n"

    with open("test.md", "w") as f:
        f.write(documentation)

if __name__ == "__main__":
    main()







