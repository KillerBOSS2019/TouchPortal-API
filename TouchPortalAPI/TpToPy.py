import json
import re
from pathlib import Path


class TpToPy():
    def __init__(self, entry):
        self.entry = json.loads(Path(entry).resolve().read_text())
        self.structState = {}
        self.structAction = {}
        self.structEvent = {}
        self.structConnector = {}
        self.structCalegories = {}
    
    def getPluginId(self):
        return self.entry.get("id", "")

    def __convertData(self, data):
        newData = {}
        if isinstance(data, list):
            for item in range(len(data)):
                newData[item] = data[item]
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

        settings = self.entry.get("settings", [])

        if isinstance(settings, list):
            for setting in range(len(settings)):
                generatedSetting[setting+1] = settings[setting]
        return generatedSetting

    def generateStates(self, data, category):
        startIndex = len(self.structState)

        for state in data:
            self.structState[startIndex] = state
            self.structState[startIndex]["category"] = category

            startIndex += 1
        

    def generateActions(self, data, category):
        startIndex = len(self.structAction)

        for action in data:
            startIndex += 1
            self.structAction[startIndex] = action
            if self.structAction[startIndex].get("format", False):
                self.structAction[startIndex]['format'] = self.__convertFormat(action["format"], action['data'])
            if action.get('data', False):
                self.structAction[startIndex]['data'] = self.__convertData(action['data'])
            self.structAction[startIndex]["category"] = category

    def generateEvents(self, data, category):
        startIndex = len(self.structEvent)

        for event in data:
            self.structEvent[startIndex] = event
            self.structEvent[startIndex]["category"] = category

    def generateConnectors(self, data, category):
        startIndex = len(self.structConnector)

        for connector in data:
            self.structConnector[startIndex] = connector
            self.structConnector[startIndex]['category'] = category
            if self.structConnector[startIndex].get('format', False):
                self.structConnector[startIndex]['format'] = self.__convertFormat(connector['format'], connector['data'])
            if connector.get("data", False):
                self.structConnector[startIndex]['data'] = self.__convertData(connector['data'])
    
    def generateCalegories(self):
        generatedCalegory = {}
        categories = self.entry.get("categories", [])

        for category in categories:
            categId = category.get("id", "").split(".")
            generatedCalegory[categId[-1]] = {
                "id": category.get("id"),
                "name": category.get("name", ""),
                "imagepath": category.get("imagepath", ""),
            }

            todoList = {"actions": self.generateActions, "states": self.generateStates,
                        "connectors": self.generateConnectors, "events": self.generateEvents}

            for todo in todoList: # hack
                if (data := category.get(todo)) and isinstance(data, list):
                    todoList[todo](data, categId[-1])
        
        return generatedCalegory

    def writetoFile(self, fileName):
        TP_PLUGIN_INFO = self.generateInfo()
        TP_PLUGIN_SETTINGS = self.generateSettings()
        TP_PLUGIN_STATES = self.structState
        TP_PLUGIN_ACTIONS = self.structAction
        TP_PLUGIN_CONNECTORS = self.structConnector
        TP_PLUGIN_EVENTS = self.structEvent
        TP_PLUGIN_CATEGORIES = self.generateCalegories()

        with open(fileName, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            for entryVar in ["TP_PLUGIN_INFO", "TP_PLUGIN_SETTINGS", "TP_PLUGIN_CATEGORIES", "TP_PLUGIN_CONNECTORS", "TP_PLUGIN_ACTIONS", "TP_PLUGIN_STATES", "TP_PLUGIN_EVENTS"]:
                struct = json.dumps(locals()[entryVar], indent=4, sort_keys=False, skipkeys=True)
                struct = re.sub(r'": (true|false)(,?)\n', lambda m: f'": {m.group(1).title()}{m.group(2)}\n', struct)
                f.write(f"{entryVar} = {struct}\n\n")

class toString():
    def __init__(self, entry):
        self.entry = TpToPy(entry)

        self.TP_PLUGIN_INFO = self.entry.generateInfo()
        self.TP_PLUGIN_SETTINGS = self.entry.generateSettings()
        self.TP_PLUGIN_CATEGORIES = self.entry.generateCalegories()
        self.TP_PLUGIN_STATES = self.entry.structState
        self.TP_PLUGIN_ACTIONS = self.entry.structAction
        self.TP_PLUGIN_CONNECTORS = self.entry.structConnector
        self.TP_PLUGIN_EVENTS = self.entry.structEvent
