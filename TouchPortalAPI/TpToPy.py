from dataclasses import dataclass
import json
from pathlib import Path

class TpToPy():
    def __init__(self, entry):
        self.entry = json.loads(Path(entry).resolve().read_text())

    def __convertData(self, data):
        newData = {}
        if isinstance(data, list):
            for item in range(len(data)):
                newData[item+1] = data[item]
        return newData

    def __convertFormat(self, actionFormat, data):
        newFormat = actionFormat
        for item in range(len(data)):
            if data[item]['id'] in actionFormat:
                newFormat = newFormat.replace("{$" + data[item]['id'] + "$}", "$[" + str(item+1) + "]")

        return newFormat

    def generateInfo(self):
        generatedInfo = {}
        infoKeys = ["sdk", "version", "name", "id", "configuration", "plugin_start_cmd_windows", "plugin_start_cmd_linux", "plugin_start_cmd_mac", "plugin_start_cmd"]

        for key in self.entry.keys():
            if key in infoKeys:
                generatedInfo[key] = self.entry[key]

        return generatedInfo
    
    def generateSettings(self):
        generatedSetting = {}
        if not self.entry.get("settings", True): return generatedSetting

        settings = self.entry["settings"]

        if isinstance(settings, list):
            for setting in range(len(settings)):
                generatedSetting[setting+1] = settings[setting]
        return generatedSetting

    def generateStates(self):
        generatedState = {}
        categories = self.entry["categories"]

        for category in range(len(categories)):
            if categories[category].get("states") and isinstance(categories[category]['states'], list):
                for state in range(len(categories[category]["states"])):
                    generatedState[state+1] = categories[category]["states"][state]
                    generatedState[state+1]["category"] = categories[category]["id"]
        return generatedState
        

    def generateActions(self):
        generatedAction = {}
        categories = self.entry["categories"]

        for category in range(len(categories)):
            if categories[category].get("actions") and isinstance(categories[category]['actions'], list):
                for action in range(len(categories[category]["actions"])):
                    generatedAction[action+1] = categories[category]["actions"][action]
                    if categories[category]["actions"][action]['data']:
                        generatedAction[action+1]['format'] = self.__convertFormat(categories[category]["actions"][action]['format'], generatedAction[action+1]['data'])
                        generatedAction[action+1]['data'] = self.__convertData(categories[category]["actions"][action]['data'])

                    generatedAction[action+1]["category"] = categories[category]["id"]
        return generatedAction

    def generateEvents(self):
        generatedEvents = {}
        categories = self.entry["categories"]

        for category in range(len(categories)):
            if categories[category].get("events") and isinstance(categories[category]['events'], list):
                for event in range(len(categories[category]["events"])):
                    generatedEvents[event+1] = categories[category]["events"][event]
                    generatedEvents[event+1]["category"] = categories[category]["id"]

        return generatedEvents

    def generateConnectors(self):
        generatedConnectors = {}
        categories = self.entry["categories"]
        for category in range(len(categories)):
            if categories[category].get("connectors") and isinstance(categories[category]['connectors'], list):
                for connector in range(len(categories[category]["connectors"])):
                    generatedConnectors[connector+1] = categories[category]["connectors"][connector]
                    generatedConnectors[connector+1]["category"] = categories[category]["id"]
                    if generatedConnectors[connector+1].get('data', False):
                        generatedConnectors[connector+1]['format'] = self.__convertFormat(generatedConnectors[connector+1]['format'], generatedConnectors[connector+1]['data'])
                        generatedConnectors[connector+1]['data'] = self.__convertData(generatedConnectors[connector+1]['data'])
        
        return generatedConnectors

    def writetoFile(self, fileName):
        TP_PLUGIN_INFO = self.generateInfo()
        TP_PLUGIN_SETTINGS = self.generateSettings()
        TP_PLUGIN_STATES = self.generateStates()
        TP_PLUGIN_ACTIONS = self.generateActions()
        TP_PLUGIN_CONNECTORS = self.generateConnectors()
        TP_PLUGIN_EVENTS = self.generateEvents()
        with open(fileName, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            for entryVar in ["TP_PLUGIN_INFO", "TP_PLUGIN_SETTINGS", "TP_PLUGIN_STATES", "TP_PLUGIN_ACTIONS", "TP_PLUGIN_CONNECTORS", "TP_PLUGIN_EVENTS"]:
                struct = json.dumps(locals()[entryVar], indent=4, sort_keys=False, skipkeys=True)
                #print(struct)
                f.write(f"{entryVar} = {struct}\n\n")

class toString():
    def __init__(self, entry):
        self.entry = TpToPy(entry)

        self.TP_PLUGIN_INFO = self.entry.generateInfo()
        self.TP_PLUGIN_SETTINGS = self.entry.generateSettings()
        self.TP_PLUGIN_STATES = self.entry.generateStates()
        self.TP_PLUGIN_ACTIONS = self.entry.generateActions()
        self.TP_PLUGIN_CONNECTORS = self.entry.generateConnectors()
        self.TP_PLUGIN_EVENTS = self.entry.generateEvents()

    