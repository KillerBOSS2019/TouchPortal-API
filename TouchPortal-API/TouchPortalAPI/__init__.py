import socket
import json
from pyee import BaseEventEmitter
from threading import Timer
import requests
import os
import base64

class TYPES:
    onHold_up = 'up'
    onHold_down = 'down'
    onConnect = 'info'
    onAction = 'action'
    onListChange = 'listChange'
    onShutdown = 'closePlugin'
    onBroadcast = 'broadcast'
    onSettingUpdate = 'settings'
    allMessage = 'any'

class Client(BaseEventEmitter):
    TPHOST = '127.0.0.1'
    TPPORT = 12136
    
    def __init__(self, pluginId):
        super().__init__()
        self.pluginId = pluginId
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__timerParseReceive = None
        self.currentStates = {}
        self.currentSettings = {}
        self.__running = False
        self.__heldActions = {}

    def __buffered_readLine(self, socket):
        line = bytearray()
        while True:
            part = self.client.recv(1)
            if part != b'\n':
                line.extend(part)
            else:
                break
        return line
        
    def __parseReceiveData(self):
        try:
            rxData = self.__buffered_readLine(self.client)
            if self.__onReceiveCallback:
                self.__timerParseReceive = Timer(0, self.__onReceiveCallback, args=(self, rxData)).start()
                self.__timerParseReceive = Timer(0, self.__onAllMessage, args=(self, rxData)).start()
            if self.__running:
                self.__parseReceiveData()

        except Exception as e:
            print(e)
            if 'timed out' or "[WinError 10054]" or '[WinError 10038]' in str(e):
                self.__timerParseReceive = Timer(0, self.__onReceiveCallback, args=(self, b'{"type":"closePlugin"}')).start()
                pass

    def __onReceiveCallback(self, data, rawData: bytes):
        data = json.loads(rawData.decode())
        try:
            if data['type'] == "down":
                self.__heldActions[data['actionId']] = True
            elif data['type'] == "up":
                del self.__heldActions[data['actionId']]
        except KeyError:
            pass
        self.emit(data["type"], self.client, data)

    def __onAllMessage(self, client, rawData):
        data = json.loads(rawData.decode())
        self.emit(TYPES.allMessage, client, data)

    def isActionBeingHeld(self, actionId):
        if actionId in self.__heldActions:
            return True
        else:
            return False

    def createState(self, stateId, description, value):
        if stateId != None and stateId != "" and description != None and description != "" and value != None and value != "":
            if stateId not in self.currentStates:
                self.send({"type": "createState", "id": stateId, "desc": description, "defaultValue": value})
                self.currentStates[stateId] = value
            else:
                self.stateUpdate(stateId, value)

    def removeState(self, stateId):
        if stateId in self.currentStates:
            self.send({"type": "removeState", "id": stateId})
            self.currentStates.pop(stateId)
        else:
            raise Exception(f"{stateId} Does not exist.")

    def choiceUpdate(self, choiceId, values):
        if type(values) == type(['a','b','c']):
            self.send({"type": "choiceUpdate", "id": choiceId, "value": values})
        else:
            raise Exception(f'values argument needs to be a list not a {type(values)}')

    def choiceUpdateSpecific(self, stateId, values, instanceId):
        if type(values) == type(['a','b','c']):
            self.send({"type": "choiceUpdate", "id": stateId, "instanceId": instanceId, "value": values})
        else:
            raise Exception(f"values argument needs to be a list not a {type(values)}")

    def settingUpdate(self, settingName, settingValue):
        if settingName not in self.currentSettings or self.currentSettings[settingName] != settingValue:
            self.send({"type": "settingUpdate", "name": settingName, "value": settingValue})
            self.currentSettings[settingName] = settingValue

    def stateUpdate(self, stateId, stateValue):
        if stateId not in self.currentStates or self.currentStates[stateId] != stateValue:
            self.send({"type": "stateUpdate", "id": stateId, "value": stateValue})
            self.currentStates[stateId] = stateValue
    
    def stateUpdateMany(self, states):
        if type(states) == type(['a','b','c']):
            for state in states:
                self.stateUpdate(state['id'], state['value'])
        else:
            raise Exception(f'StateUpdateMany() takes in a list Not a {type(states)}')
        
    def updateActionData(self, instanceId, stateId, minValue, maxValue):
        '''
        TouchPortal currently only supports data.type "number"
        '''
        self.send({"type": "updateActionData", "instanceId": instanceId, data: {"minValue": minValue, "maxValue": maxValue, "id": stateId, "type": "number"}})
        
        
    def send(self, data):
        '''
        This manages the massage to send
        '''
        self.client.sendall((json.dumps(data)+'\n').encode())
        
        
    def connect(self):
        '''
        This is mainly used for connecting to TP Server
        '''
        try:
            self.client.connect((self.TPHOST, self.TPPORT))
            self.__running = True
        except ConnectionRefusedError:
            raise Exception("Failed to connect to TouchPortal")
        self.send({"type":"pair", "id": self.pluginId})
        self.__parseReceiveData()

    def disconnect(self):
        '''
        This closes the Socket
        '''
        self.client.shutdown(1)
        self.client.close()
        self.__running = False


class Tools():
    def convertImage_to_base64(image):
        '''
        It can be URL or Image path
        '''
        if os.path.isfile(image):
            with open(image, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        else:
            try:
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                r = requests.head(image)
                if r.headers['content-type'] in image_formats:
                    return base64.b64encode(requests.get(image).content).decode('utf-8')
                else:
                    print(something) # to cause undefined error so it raise Error
            except Exception as e:
                if 'Invalid' in str(e).split() or 'defined' in str(e).split():
                    raise Exception("Please pass in a URL with image in it or a file path")
        
    def updateCheck(name, repository, thisversion):
        baselink = f'https://api.github.com/repos/{name}/{repository}/tags'
        try:
            if requests.get(baselink).json()[0] == thisversion:
                return 'No updates'
            else:
                return requests.get(baselink).json()[0]
        except:
            raise Exception('Invalid Profile or Repository. Please enter your name, Repository, and the current version')
