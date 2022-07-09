"""
# TouchPortal Python TPP documentation generator

## Features

This SDK tools will generate a markdown file that can be used to document your TouchPortal plugin.

This is what it includes:
- automatically generate a table of contents
- automatically generate a badges that shows total downloads, forks, stars and license
- automatically generate action section and show details of each data
- automatically generate connector section and show details of each data
- automatically generate state section
- automatically generate event section
- automatically generate settings section
- automatically generate installation section (if you include `"doc": {"install": ""})` in `TP_PLUGIN_INFO`)
- automatically generate bugs and support section

Using it in [example](https://github.com/KillerBOSS2019/TouchPortal-API/tree/main/examples)

```
tppdoc plugin_example.py
```
In this example we are using `plugin_example.py` file because that file contains entry infomations and using those information we can generate a markdown file.

## Command-line Usage
The script command is `tppdoc` when the TouchPortalAPI is installed (via pip or setup), or `tppdoc.py` when run directly from this source.

```
<script-command> [-h] [-i] [-o OUTPUT] <target>

Script to automatically generates a documentation for a TouchPortal plugin.

positional arguments:
  <target>              tppdoc is a documanentation generator for TouchPortal plugins. It uses py entry to generates a markdown file.It
                        can generate a table for the plugin settings, connectors, actions, state, and event. and It will also show data
                        field example, It can show max length, min value, max value for the data field.

options:
  -h, --help            show this help message and exit
  -i, --ignoreError     Ignore error when validating. Default is False.
  -o OUTPUT, --output OUTPUT Name of generated documentation. Default is "Documentation". You do not need to add the extension.
```
"""

__copyright__ = """
This file is part of the TouchPortal-API project.
Copyright TouchPortal-API Developers
Copyright (c) 2021 DamienS
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

import sys, os
import importlib
from argparse import ArgumentParser

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from sdk_tools import _validateDefinition, generateDefinitionFromScript
import TpToPy

def getInfoFromBuildScript(script:str):
	try:
		sys.path.insert(1, os.getcwd()) # This allows build config to import stuff
		spec = importlib.util.spec_from_file_location("entry", script)
		entry = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(entry)
	except Exception as e:
		raise ImportError(f"ERROR while trying to import entry code from '{script}': {repr(e)}")
	return entry

def generateCategoryLink(linkType, entry, categoryStruct):
    linkList = []
    # Ik this is not the most efficient way to do it
    for category in categoryStruct:
        for item in entry:
            if (theItem := entry[item].get('category')) == category:
                linkName = categoryStruct[theItem].get('name')
                linkAdress = categoryStruct[theItem].get('id') + linkType
                if (dataToAppend := f"\n        - [{linkName}](#{linkAdress})") not in linkList:
                    linkList.append(dataToAppend)

    # print(linkList)
    return "".join(linkList)

def generateTableContent(entry, entryFile):
    table_content = f"""
# {entry['name'].replace(" ", "-")}"""
    if entry.get('doc') and (repository := entry['doc'].get("repository")) and repository.find(":") != -1:
        table_content += f"""
![Downloads](https://img.shields.io/github/downloads/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]}/total) 
![Forks](https://img.shields.io/github/forks/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]}) 
![Stars](https://img.shields.io/github/stars/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]}) 
![License](https://img.shields.io/github/license/{entry['doc']['repository'].split(":")[0]}/{entry['doc']['repository'].split(":")[1]})
"""

    table_content += f"""
- [{entry['name']}](#{entry['name'].replace(" ", "-")})
  - [Description](#description)"""
    if hasattr(entryFile, "TP_PLUGIN_SETTINGS") and entryFile.TP_PLUGIN_SETTINGS:
        table_content += """ \n  - [Settings Overview](#Settings-Overview)"""

    table_content += """
  - [Features](#Features)"""

    if "TP_PLUGIN_ACTIONS" in dir(entryFile) and entryFile.TP_PLUGIN_ACTIONS:
        table_content += """\n    - [Actions](#actions)"""

        table_content += generateCategoryLink("actions", entryFile.TP_PLUGIN_ACTIONS, entryFile.TP_PLUGIN_CATEGORIES)

    if "TP_PLUGIN_CONNECTORS" in dir(entryFile) and entryFile.TP_PLUGIN_CONNECTORS:
        table_content += """
    - [Connectors](#connectors)"""
        table_content += generateCategoryLink("connectors", entryFile.TP_PLUGIN_CONNECTORS, entryFile.TP_PLUGIN_CATEGORIES)

    if "TP_PLUGIN_STATES" in dir(entryFile) and entryFile.TP_PLUGIN_STATES:
        table_content += """
    - [States](#states)"""
        table_content += generateCategoryLink("states", entryFile.TP_PLUGIN_STATES, entryFile.TP_PLUGIN_CATEGORIES)

    if "TP_PLUGIN_EVENTS" in dir(entryFile) and entryFile.TP_PLUGIN_EVENTS:
        table_content += """
    - [Events](#events)"""
        table_content += generateCategoryLink("events", entryFile.TP_PLUGIN_EVENTS, entryFile.TP_PLUGIN_CATEGORIES)

    if entry.get("doc") and entry['doc'].get("Install"):
        table_content += """
  - [Installation Guide](#installation)"""
        
    table_content += """
  - [Bugs and Support](#bugs-and-suggestion)
  - [License](#license)
  """
    return table_content

def typeNumber(entry):
    typeDoc = ""
    if entry.get('minValue'):
        typeDoc += f" &nbsp; <b>Min Value:</b> {entry['minValue']}"
    else:
        typeDoc += " &nbsp; <b>Min Value:</b> -2147483648"

    if entry.get('maxValue'):
        typeDoc += f" &nbsp; <b>Max Value:</b> {entry['maxValue']}"
    else:
        typeDoc += f" &nbsp; <b>Max Value:</b> 2147483647"

    if entry.get('allowDecimals'):
        typeDoc += f" &nbsp; <b>Allow Decimals:</b> {entry['allowDecimals']}"

    return typeDoc

def __generateData(entry):
    dataDocList = ""
    needDropdown = False
    if entry.get('data'):
        dataDocList += "<td><ol start=1>"
        if len(entry['data']) > 3:
            dataDocList = "<td><details><summary><ins>Click to expand</ins></summary><ol start=1>\n"
            needDropdown = True
        for data in entry['data']:
            dataDocList += f"<li>Type: {entry['data'][data]['type']} &nbsp; \n"

            if entry['data'][data]['type'] == "choice" and entry['data'][data].get('valueChoices'):
                dataDocList += f"Default: <b>{entry['data'][data]['default']}</b> Possible choices: {entry['data'][data]['valueChoices']}"
            elif "default" in entry['data'][data].keys() and entry['data'][data]['default'] != "":
                dataDocList += f"Default: <b>{entry['data'][data]['default']}</b>"
            else:
                dataDocList += "&lt;empty&gt;"

            if entry['data'][data]['type'] == "number":
                dataDocList += typeNumber(entry['data'][data])

            dataDocList += "</li>\n"
        dataDocList += "</ol></td>\n"
        if needDropdown:
            dataDocList += "</details>"
    else:
        dataDocList += "<td> </td>\n"
    
    return dataDocList

def getCategoryName(categoryId, categoryStruct):
    try:
        return categoryStruct[categoryId].get('name', categoryId)
    except IndexError:
        return categoryStruct[list(categoryStruct.keys())[0]] # If it does not have a `category` field It will use default

def getCategoryId(categoryId, categoryStruct):
    return categoryStruct.get(categoryId)

def generateAction(entry, categoryStruct):
    actionDoc = "\n## Actions\n"
    filterActionbyCategory = {}

    numberOfCategory = [entry[x].get("category", "main") for x in entry]
    allowDetailOpen = not len(set(numberOfCategory)) > 1

    for action in entry:
        categoryName = entry[action].get("category", "main")
        if entry[action]['category'] not in filterActionbyCategory:
            filterActionbyCategory[categoryName] = "<table>\n"
            filterActionbyCategory[categoryName] += "<tr valign='buttom'>" + "<th>Action Name</th>" + "<th>Description</th>" + "<th>Format</th>" + \
                "<th nowrap>Data<br/><div align=left><sub>choices/default (in bold)</th>" + \
                "<th>On<br/>Hold</sub></div></th>" + \
                "</tr>\n"

        filterActionbyCategory[categoryName] += f"<tr valign='top'><td>{entry[action]['name']}</td>" + \
        f"<td>{entry[action]['doc'] if entry[action].get('doc') else ' '}</td>" + \
        f"<td>{entry[action]['format'].replace('$', '') if entry[action].get('format') else ' '}</td>"
        filterActionbyCategory[categoryName] += __generateData(entry[action])

        filterActionbyCategory[categoryName] += f"<td align=center>{'Yes' if entry[action].get('hasHoldFunctionality') and entry[action]['hasHoldFunctionality'] else 'No'}</td>\n"
    
    for category in filterActionbyCategory:
        categoryRealName = getCategoryName(categoryId=category, categoryStruct=categoryStruct)
        categoryLinkAddress = getCategoryId(category, categoryStruct).get("id") + "actions" # to make it unique
        actionDoc += f"<details {'open' if list(filterActionbyCategory.keys()).index(category) == 0 and allowDetailOpen else ''} id='{categoryLinkAddress}'><summary><b>Category:</b> {categoryRealName} <small><ins>(Click to expand)</ins></small></summary>"
        actionDoc += filterActionbyCategory[category]
        actionDoc += "</tr></table></details>\n"
    
    actionDoc += "<br>\n"
    return actionDoc

def generateConnectors(entry, categoryStruct):
    connectorDoc = "\n## Connectors\n"
    filterConnectorsbyCategory = {}

    numberOfCategory = [entry[x].get("category", "main") for x in entry]
    allowDetailOpen = not len(set(numberOfCategory)) > 1

    for connector in entry:
        categoryName = entry[connector].get("category", "main")
        if entry[connector]['category'] not in filterConnectorsbyCategory:
            filterConnectorsbyCategory[categoryName] = "<table>\n"
            filterConnectorsbyCategory[categoryName] += "<tr valign='buttom'>" + "<th>Slider Name</th>" + "<th>Description</th>" + "<th>Format</th>" + \
                                                        "<th nowrap>Data<br/><div align=left><sub>choices/default (in bold)</th>" + "</tr>\n"
            
        filterConnectorsbyCategory[categoryName] += f"<tr valign='top'><td>{entry[connector]['name']}</td>" + \
        f"<td>{entry[connector]['doc'] if entry[connector].get('doc') else ' '}</td>" + \
        f"<td>{entry[connector]['format'].replace('$', '') if entry[connector].get('format') else ' '}</td>"

        filterConnectorsbyCategory[categoryName] += __generateData(entry[connector])

    for category in filterConnectorsbyCategory:
        categoryRealName = getCategoryName(categoryId=category, categoryStruct=categoryStruct)
        categoryLinkAddress = getCategoryId(category, categoryStruct).get("id") + "connectors"
        connectorDoc += f"<details {'open' if list(filterConnectorsbyCategory.keys()).index(category) == 0 and allowDetailOpen else ''} id='{categoryLinkAddress}'><summary><b>Category:</b> {categoryRealName} <small><ins>(Click to expand)</ins></small></summary>"
        connectorDoc += filterConnectorsbyCategory[category]
        connectorDoc += "</table></details>\n"
    connectorDoc += "<br>\n"

    return connectorDoc
    


def generateSetting(entry):
    settingDoc = "\n\n## Settings Overview\n"

    def f(data):
        return [data.get('maxLength', 0) > 0, data.get('minValue', None), data.get('maxValue', None)]

    for setting in entry.keys():
        settingDoc += "| Read-only | Type | Default Value"
        if f(entry[setting])[0]: settingDoc += f" | Max. Length"
        if f(entry[setting])[1]: settingDoc += f" | Min. Value"
        if f(entry[setting])[2]: settingDoc += f" | Max. Value"
        settingDoc += " |\n"
        settingDoc += "| --- | --- | ---"
        if f(entry[setting])[0]: settingDoc += f" | ---"
        if f(entry[setting])[1]: settingDoc += f" | ---"
        if f(entry[setting])[2]: settingDoc += f" | ---"

        settingDoc += " |\n"
        settingDoc += f"| {entry[setting].get('readOnly', False)} | {entry[setting]['type']} | {entry[setting]['default']}"
        if f(entry[setting])[0]: settingDoc += f" | {entry[setting]['maxLength']}"
        if f(entry[setting])[1]: settingDoc += f" | {entry[setting]['minValue']}"
        if f(entry[setting])[2]: settingDoc += f" | {entry[setting]['maxValue']}"
        settingDoc += " |\n\n"
        if entry[setting].get('doc'):
            settingDoc += f"{entry[setting]['doc']}\n\n"
    return settingDoc 

def generateState(entry, baseid, categoryStruct):
    stateDoc = "\n## States\n"
    filterCategory = {}
    
    numberOfCategory = [entry[x].get("category", "main") for x in entry]
    allowDetailOpen = not len(set(numberOfCategory)) > 1

    for state in entry:
        categoryName = entry[state].get("category", "main")
        state = entry[state]
        if not categoryName in filterCategory:
            categoryRealName = getCategoryName(categoryId=state.get('category'), categoryStruct=categoryStruct)
            categoryLinkAddress = getCategoryId(state.get('category'), categoryStruct).get("id") + "states"
            filterCategory[categoryName] = ""
            filterCategory[categoryName] += f"<details{' open' if len(filterCategory) == 1 and allowDetailOpen else ''} id='{categoryLinkAddress}'><summary><b>Category:</b> {categoryRealName} <small><ins>(Click to expand)</ins></small></summary>\n"
            filterCategory[categoryName] += "\n\n| Id | Description | DefaultValue | parentGroup |\n"
            filterCategory[categoryName] += "| --- | --- | --- | --- |\n"

        filterCategory[categoryName] += f"| {state['id'].split(baseid)[-1]} | {state['desc']} | {state['default']} | {state.get('parentGroup', ' ')} |\n"

    for category in filterCategory:
        stateDoc += filterCategory[category]
        stateDoc += "</details>\n\n"
    stateDoc += "<br>\n"

    return stateDoc

def generateEvent(entry, baseid, categoryStruct):
    eventDoc = "\n## Events\n\n"
    filterCategory = {}
    numberOfCategory = [entry[x].get("category", "main") for x in entry]
    allowDetailOpen = not len(set(numberOfCategory)) > 1
    for event in entry:
        event = entry[event] # dict looks like {'0': {}, '1': {}}. so when looping It will give `0` etc..
        needDropdown = False

        categoryName = event.get("category", "main")
        if not categoryName in filterCategory:
            categoryRealName = getCategoryName(categoryId=categoryName, categoryStruct=categoryStruct)
            categoryLinkAddress = getCategoryId(categoryName, categoryStruct).get("id") + "events"
            filterCategory[categoryName] = ""
            filterCategory[categoryName] += f"<details{' open' if len(filterCategory) == 1 and allowDetailOpen else ''} id='{categoryLinkAddress}'><summary><b>Category: </b>{categoryRealName} <small><ins>(Click to expand)</ins></small></summary>\n\n"
            filterCategory[categoryName] += "<table>\n"
            filterCategory[categoryName] += "<tr valign='buttom'>" + "<th>Id</th>" + "<th>Name</th>" + "<th nowrap>Evaluated State Id</th>" + \
                                                 "<th>Format</th>" + "<th>Type</th>" + "<th>Choice(s)</th>" + "</tr>\n"

        filterCategory[categoryName] += f"<tr valign='top'><td>{event['id'].split(baseid)[-1]}</td>" + \
            f"<td>{event.get('name', '')}</td>" + \
            f"<td>{event.get('valueStateId', '').split(baseid)[-1]}</td>" + \
            f"<td>{event.get('format', '')}</td>" + \
            f"<td>{event.get('valueType', '')}</td>" + \
            "<td>"
        
        if len(event.get('valueChoices', [])) > 5:
            filterCategory[categoryName] += f"<details><summary><ins>detail</ins></summary>\n"
            needDropdown = True

        filterCategory[categoryName] += f"<ul>"
        for item in event.get('valueChoices', []):
            filterCategory[categoryName] += f"<li>{item}</li>"
        filterCategory[categoryName] += "</ul></td>"

        if needDropdown:
            filterCategory[categoryName] += "</details>"
        eventDoc += "<td></tr>\n"
    
    for category in filterCategory:
        eventDoc += filterCategory[category]
        eventDoc += f"</table></details>\n"
    eventDoc += "<br>\n"

    return eventDoc

def main(docArg=None):
    parser = ArgumentParser(description=
        "Script to automatically generates a documentation for a TouchPortal plugin.")

    parser.add_argument(
        "target", metavar='<target>', type=str,
        help='tppdoc is a documanentation generator for TouchPortal plugins. It uses py entry to generates a markdown file.' + \
            'It can generate a table for the plugin settings, connectors, actions, state, and event. and It will also show' + \
                ' data field example, It can show max length, min value, max value for the data field.'
    )

    parser.add_argument(
        "-i", "--ignoreError", action='store_true', default=False,
        help='Ignore error when validating. Default is False.'
    )

    parser.add_argument(
        "-o", "--output", default="Documentation.md",
        help='Name of generated documentation. Default is "Documentation". You do not need to add the extension.'
    )

    opts = parser.parse_args(docArg)
    del parser

    out_dir = os.path.dirname(opts.target)
    targetPathbaseName = os.path.basename(opts.target)

    if out_dir:
        os.chdir(out_dir)

    entryType = "py" if targetPathbaseName.endswith(".py") else "tp"
    if not opts.ignoreError:
        print("vaildating entry...\n")
        if  entryType == "tp" and _validateDefinition(targetPathbaseName):
            print(targetPathbaseName, "is vaild file. continue building document.\n")
        elif entryType == "py" and _validateDefinition(generateDefinitionFromScript(targetPathbaseName), as_str=True):
            print(targetPathbaseName, "is vaild file. continue building document.\n")
        else:
            print("File is invalid. Please above error for more information.")
            return -1
    else:
        print("Ignoring errors, contiune building document.\n")

    if entryType == "py": entry = getInfoFromBuildScript(targetPathbaseName)
    else: entry = TpToPy.toString(targetPathbaseName)


    documentation = """"""

    print("Building table of content\n")
    tableContent = generateTableContent(entry.TP_PLUGIN_INFO, entry)
    documentation += tableContent

    documentation += f"""
# Description

"""
    if entry.TP_PLUGIN_INFO.get('doc') and entry.TP_PLUGIN_INFO['doc'].get('description'):
        documentation += f"{entry.TP_PLUGIN_INFO['doc']['description']}\n\n"
    
    documentation += f"This documentation generated for {entry.TP_PLUGIN_INFO['name']} V{entry.TP_PLUGIN_INFO['version']} with [Python TouchPortal SDK](https://github.com/KillerBOSS2019/TouchPortal-API)."
    if entry.TP_PLUGIN_SETTINGS:
        print("Generating settings section\n")
        setting = generateSetting(entry.TP_PLUGIN_SETTINGS)
        documentation += setting

    documentation += "\n# Features\n"
    categoryStruct = entry.TP_PLUGIN_CATEGORIES

    if "TP_PLUGIN_ACTIONS" in dir(entry) and entry.TP_PLUGIN_ACTIONS:
        print("Generating action section\n")
        action = generateAction(entry.TP_PLUGIN_ACTIONS, categoryStruct)
        documentation += action


    if "TP_PLUGIN_CONNECTORS" in dir(entry) and entry.TP_PLUGIN_CONNECTORS:
        print("Generating connector section\n")
        connector = generateConnectors(entry.TP_PLUGIN_CONNECTORS, categoryStruct)
        documentation += connector

    if "TP_PLUGIN_STATES" in dir(entry) and entry.TP_PLUGIN_STATES:
        print("Generating state section\n")
        state = generateState(entry.TP_PLUGIN_STATES, entry.TP_PLUGIN_INFO['id'], categoryStruct)
        documentation += state

    if "TP_PLUGIN_EVENTS" in dir(entry) and entry.TP_PLUGIN_EVENTS:
        print("Generating event section\n")
        event = generateEvent(entry.TP_PLUGIN_EVENTS, entry.TP_PLUGIN_INFO['id'], categoryStruct)
        documentation += event

    if entry.TP_PLUGIN_INFO.get("doc") and entry.TP_PLUGIN_INFO['doc'].get('Install'):
        print("Found install method. Generating install section\n")
        documentation += "\n# Installation\n"
        documentation += entry.TP_PLUGIN_INFO['doc']['Install']

    print("Generating Bugs and Suggestion section\n")
    documentation += "\n# Bugs and Suggestion\n"
    try:
        documentation += f"Open an [issue](https://github.com/{'/'.join(entry.TP_PLUGIN_INFO['doc']['repository'].split(':'))}/issues) or join offical [TouchPortal Discord](https://discord.gg/MgxQb8r) for support.\n\n"
    except:
        documentation += f"Open an issue on github or join offical [TouchPortal Discord](https://discord.gg/MgxQb8r) for support.\n\n"

    documentation += "\n# License\n"
    documentation += "This plugin is licensed under the [GPL 3.0 License] - see the [LICENSE](LICENSE) file for more information.\n\n"

    with open(opts.output, "w") as f:
        f.write(documentation)
        
    print("Finished generating documentation.")
    return 0

if __name__ == "__main__":
    sys.exit(main())