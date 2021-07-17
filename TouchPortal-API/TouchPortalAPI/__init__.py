__Copyright__ = """
    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) 2021 DamienS

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

import socket
import selectors
import json
from pyee import ExecutorEventEmitter
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
import requests
import os
import base64

class TYPES:
    onHold_up = 'up'
    onHold_down = 'down'
    onConnect = 'info'
    onAction = 'action'
    onListChange = 'listChange'
    onConnectorChange = 'connectorChange'
    onShutdown = 'closePlugin'
    onBroadcast = 'broadcast'
    onSettingUpdate = 'settings'
    allMessage = 'any'
    onError = 'error'  # from ExecutorEventEmitter, emitted when an event callback raises an exception

class Client(ExecutorEventEmitter):
    '''
    A client for TouchPortal plugin integration.
    Implements a [pyee.ExecutorEventEmitter](https://pyee.readthedocs.io/en/latest/#pyee.ExecutorEventEmitter).

    Args:
        `pluginId`      (str): ID string of the TouchPortal plugin using this client.
        `sleepPeriod` (float): Seconds to sleep the event loop between socket read events (default: 0.01).
        `autoClose`    (bool): If `True` then this client will automatically disconnect when a `closePlugin` message is received from TP.
        `checkPluginId` (bool): Validate that `pluginId` matches ours in any messages from TP which contain one (such as actions). Default is `True`.
        `maxWorkers`    (int): Maximum worker threads to run concurrently for event handlers. Default of `None` creates a default-constructed `ThreadPoolExecutor`.
        `executor`   (object): Passed to `pyee.ExecutorEventEmitter`. By default this is a default-constructed
                               [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor),
                               optionally using `maxWorkers` concurrent threads.
    '''
    TPHOST = '127.0.0.1'
    TPPORT = 12136
    RCV_BUFFER_SZ = 4096   # [B] incoming data buffer size
    SND_BUFFER_SZ = 32**4  # [B] maximum size of send data buffer (1MB)
    SOCK_EVENT_TO = 1.0    # [s] timeout for selector.select() event monitor

    def __init__(self, pluginId, sleepPeriod=0.01, autoClose=False, checkPluginId=True, updateStatesOnBroadcast=True, maxWorkers=None, executor=None):
        if not executor and maxWorkers:
            executor = ThreadPoolExecutor(max_workers=maxWorkers)
        super(Client, self).__init__(executor=executor)
        self.pluginId = pluginId
        self.sleepPeriod = sleepPeriod
        self.autoClose = autoClose
        self.checkPluginId = checkPluginId
        self.updateStatesOnBroadcast = updateStatesOnBroadcast
        self.client = None
        self.selector = None
        self.currentStates = {}
        self.currentSettings = {}
        self.__heldActions = {}
        self.__stopEvent = Event()       # main loop inerrupt
        self.__stopEvent.set()           # not running yet
        self.__dataReadyEvent = Event()  # set when __sendBuffer has data
        self.__writeLock = Lock()        # mutex for __sendBuffer
        self.__sendBuffer = bytearray()
        self.__recvBuffer = bytearray()

    def __buffered_readLine(self):
        try:
            # Should be ready to read
            data = self.client.recv(self.RCV_BUFFER_SZ)
        except BlockingIOError:
            pass  # Resource temporarily unavailable (errno EWOULDBLOCK)
        except OSError:
            raise  # No connection
        else:
            if data:
                lines = []
                self.__recvBuffer += data
                while (i := self.__recvBuffer.find(b'\n')) > -1:
                    lines.append(self.__recvBuffer[:i])
                    del self.__recvBuffer[:i+1]
                return lines
            else:
                # No connection
                raise RuntimeError("Peer closed the connection.")
        return []

    def __write(self):
        if self.client and self.__sendBuffer and self.__getWriteLock():
            try:
                # Should be ready to write
                sent = self.client.send(self.__sendBuffer)
            except BlockingIOError:
                pass  # Resource temporarily unavailable (errno EWOULDBLOCK)
            except OSError:
                raise  # No connection
            else:
                del self.__sendBuffer[:sent]
            finally:
                if not self.__sendBuffer:
                    self.__dataReadyEvent.clear()
                self.__writeLock.release()

    def __run(self):
        try:
            while not self.__stopEvent.is_set():
                events = self.selector.select(timeout=self.SOCK_EVENT_TO)
                if self.__stopEvent.is_set():  # may be set while waiting for selector events (unlikely)
                    break
                for _, mask in events:
                    if (mask & selectors.EVENT_READ):
                        for line in self.__buffered_readLine():
                            self.__processMessage(line)
                    if (mask & selectors.EVENT_WRITE):
                        self.__write()
                # Sleep for period or until there is data in the write buffer.
                # In theory if data is constantly avaiable, this could block,
                # in which case it may be better to self.__stopEvent.wait()
                if self.__dataReadyEvent.wait(self.sleepPeriod):
                    continue
                continue
        except Exception as e:
            self.__die(f"Exception in client event loop: {repr(e)}", e)

    def __processMessage(self, message: bytes):
        data = json.loads(message.decode())
        if data and (act_type := data.get('type')):
            if self.checkPluginId and (pid := data.get('pluginId')) and pid != self.pluginId:
                return
            if act_type == TYPES.onShutdown:
                if self.autoClose: self.__close()
            elif act_type == TYPES.onHold_down and (aid := data.get('actionId')):
                self.__heldActions[aid] = True
            elif act_type == TYPES.onHold_up and (aid := data.get('actionId')):
                del self.__heldActions[aid]
            elif act_type == TYPES.onBroadcast and self.updateStatesOnBroadcast:
                for key, value in self.currentStates.items():
                    self.__stateUpdate(key, value, True)
            self.__emitEvent(act_type, data)

    def __emitEvent(self, ev, data):
        self.emit(ev, data)
        self.emit(TYPES.allMessage, data)

    def __open(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.selector = selectors.DefaultSelector()
            self.client.connect((self.TPHOST, self.TPPORT))
        except Exception:
            self.selector = self.client = None
            raise
        self.client.setblocking(False)
        self.selector.register(self.client, (selectors.EVENT_READ | selectors.EVENT_WRITE))
        self.__stopEvent.clear()

    def __close(self):
        self.__stopEvent.set()
        if self.__writeLock.locked():
            self.__writeLock.release()
        self.__sendBuffer.clear()
        if not self.selector:
            return
        if self.selector.get_map():
            try:
                self.selector.unregister(self.client)
            except Exception as e:
                print(f"Error in selector.unregister(): {repr(e)}")
        try:
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
        except OSError as e:
            print(f"Error in socket.close(): {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection, socket cannot be reused anyway.
            self.client = None
        self.selector.close()
        self.selector = None
        # print("TP Client stopped.")

    def __die(self, msg=None, exc=None):
        if msg: print(msg)
        self.__emitEvent(TYPES.onShutdown, {"type": TYPES.onShutdown})
        self.__close()
        if exc: raise exc

    def __getWriteLock(self):
        if self.__writeLock.acquire(timeout=15):
            if self.__stopEvent.is_set():
                if self.__writeLock.locked(): self.__writeLock.release()
                return False
            return True
        self.__die(exc=RuntimeError("Send buffer mutex deadlock, cannot continue."))
        return False

    def isConnected(self):
        return not self.__stopEvent.is_set()

    def isActionBeingHeld(self, actionId:str):
        return actionId in self.__heldActions

    def createState(self, stateId:str, description:str, value:str):
        if stateId and description and value != None:
            if stateId not in self.currentStates:
                self.send({"type": "createState", "id": stateId, "desc": description, "defaultValue": value})
                self.currentStates[stateId] = value
            else:
                self.stateUpdate(stateId, value)

    def createStateMany(self, states:list):
        try:
            for state in states:
                if isinstance(state, dict):
                    self.createState(state.get('id', ""), state.get('desc', ""), state.get('value', ""))
                else:
                    raise TypeError(f'createStateMany() requires a list of dicts, got {type(state)} instead.')
        except:
            raise TypeError(f'createStateMany() requires an iteratable, got {type(states)} instead.')

    def removeState(self, stateId:str, validateExists = True):
        if stateId and stateId in self.currentStates:
            self.send({"type": "removeState", "id": stateId})
            self.currentStates.pop(stateId)
        elif validateExists:
            raise Exception(f"{stateId} Does not exist.")

    def removeStateMany(self, states:list):
        try:
            for state in states:
                self.removeState(state, False)
        except TypeError:
            raise TypeError(f'removeStateMany() requires an iteratable, got {type(states)} instead.')

    def choiceUpdate(self, choiceId:str, values:list):
        if choiceId:
            if isinstance(values, list):
                self.send({"type": "choiceUpdate", "id": choiceId, "value": values})
            else:
                raise TypeError(f'choiceUpdate() values argument needs to be a list not a {type(values)}')

    def choiceUpdateSpecific(self, stateId:str, values:list, instanceId:str):
        if stateId and instanceId:
            if isinstance(values, list):
                self.send({"type": "choiceUpdate", "id": stateId, "instanceId": instanceId, "value": values})
            else:
                raise TypeError(f'choiceUpdateSpecific() values argument needs to be a list not a {type(values)}')

    def settingUpdate(self, settingName:str, settingValue):
        if settingName and settingName not in self.currentSettings or self.currentSettings[settingName] != settingValue:
            self.send({"type": "settingUpdate", "name": settingName, "value": settingValue})
            self.currentSettings[settingName] = settingValue

    def stateUpdate(self, stateId:str, stateValue:str):
        self.__stateUpdate(stateId, stateValue, False)
        
    def __stateUpdate(self, stateId:str, stateValue:str, forced:bool):
        if stateId:
            if forced or stateId not in self.currentStates or self.currentStates[stateId] != stateValue:
                self.send({"type": "stateUpdate", "id": stateId, "value": stateValue})
            self.currentStates[stateId] = stateValue

    def stateUpdateMany(self, states:list):
        try:
            for state in states:
                if isinstance(state, dict):
                    self.stateUpdate(state.get('id', ""), state.get('value', ""))
                else:
                    raise TypeError(f'StateUpdateMany() requires a list of dicts, got {type(state)} instead.')
        except TypeError:
            raise TypeError(f'StateUpdateMany() requires an iteratable, got {type(states)} instead.')

    def updateActionData(self, instanceId:str, stateId:str, minValue, maxValue):
        '''
        TouchPortal currently only supports data.type "number"
        '''
        self.send({"type": "updateActionData", "instanceId": instanceId, "data": {"minValue": minValue, "maxValue": maxValue, "id": stateId, "type": "number"}})

    def send(self, data):
        '''
        This manages the massage to send
        '''
        if self.__getWriteLock():
            if len(self.__sendBuffer) + len(data) > self.SND_BUFFER_SZ:
                self.__writeLock.release()
                raise ResourceWarning("TP Client send buffer is full!")
            self.__sendBuffer += (json.dumps(data)+'\n').encode()
            self.__writeLock.release()
            self.__dataReadyEvent.set()

    def connect(self):
        '''
        This is mainly used for connecting to TP Server.
        If successful, it starts the main processing loop of this client.
        Does nothing if client is already connected.
        '''
        if not self.isConnected():
            self.__open()
            self.send({"type":"pair", "id": self.pluginId})
            self.__run()  # start the event loop

    def disconnect(self):
        '''
        This closes the connection to TP and terminates the client processing loop.
        Does nothing if client is already disconnected.
        '''
        if self.isConnected():
            self.__close()

    @staticmethod
    def getActionDataValue(data:list, valueId:str=None):
        '''
        Utility for processing action messages from TP. For example:
            {"type": "action", "data": [{ "id": "data object id", "value": "user specified value" }, ...]}

        Returns the `value` with specific `id` from a list of action data,
        or `None` if the `id` wasn't found. If a null id is passed in `valueId`
        then the first entry which has a `value` key, if any, will be returned.

        Args:
            `data`: the "data" array from a TP "action", "on", or "off" message
            `valueId`: the "id" to look for in `data`. `None` or blank to return the first value found.
        '''
        if not data: return None
        if valueId:
            return next((x.get('value') for x in data if x.get('id', '') == valueId), None)
        return next((x.get('value') for x in data if x.get('value') != None), None)


class Tools():

    @staticmethod
    def convertImage_to_base64(image, type="Auto", image_formats=["image/png", "image/jpeg", "image/jpg"]):
        '''
        `image` can be a URL or file path.
        `type` can be "Auto", "Web" (for URL), or "Local" (for file path).
        `image_formats` is a list of one or more MIME types to accept, used only with URLs to confirm the response is valid.
        May raise a `TypeError` if URL request returns an invalid MIME type.
        May raise a `ValueError` in other cases such as invalid URL or file path.
        '''
        data = None
        if type == "Auto" or type == "Web":
            try:
                r = requests.head(image)
                if r.headers['content-type'] in image_formats:
                    data = requests.get(image).content
                else:
                    raise TypeError(f"Returned image content type ({r.headers['content-type']}) is not one of: {image_formats}")
            except ValueError:  # raised by requests module for invalid URLs, less generic than requests.RequestException
                if type == "Auto":
                    pass
                else:
                    raise
        if not data and (type == "Auto" or type == "Local") and os.path.isfile(image):
            with open(image, "rb") as img_file:
                data = img_file.read()
        if data:
            return base64.b64encode(data).decode('ascii')
        raise ValueError(f"'{image}' is neither a valid URL nor an existing file.")

    @staticmethod
    def updateCheck(name, repository):
        '''
        Returns the newest tag name from a GitHub repository.
        `name` is the GitHub user name for the URL path.
        `repository` is the GitHub repository name for the URL path.
        May raise a `ValueError` if the repository URL can't be reached, doesn't exist, or doesn't have any tags.
        '''
        baselink = f'https://api.github.com/repos/{name}/{repository}/tags'
        if (r := requests.get(baselink)) and r.ok:
            if (js := r.json()):
                return js[0].get('name', "")
            raise ValueError(f'No tags found in repository: {baselink}')
        else:
            raise ValueError(f'Invalid repository URL or response: {baselink}')
