import socket
import selectors
import json
from pyee import EventEmitter
from threading import Timer, Event, Lock
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

class Client(EventEmitter):
    TPHOST = '127.0.0.1'
    TPPORT = 12136
    RCV_BUFFER_SZ = 4096   # [B] incoming data buffer size
    SND_BUFFER_SZ = 32**4  # [B] maximum size of send data buffer (1MB)
    SLEEP_PERIOD = 0.01    # [s] event loop sleep between socket read events
    SOCK_EVENT_TO = 1.0    # [s] timeout for selector.select() event monitor

    def __init__(self, pluginId):
        super().__init__()
        self.pluginId = pluginId
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
                            Timer(0, self.__onReceiveCallback, args=[line]).start()
                            Timer(0, self.__onAllMessage, args=[line]).start()
                    if (mask & selectors.EVENT_WRITE):
                        self.__write()
                # Sleep for period or until there is data in the write buffer.
                # In theory if data is constantly avaiable, this could block,
                # in which case it may be better to self.__stopEvent.wait()
                if self.__dataReadyEvent.wait(self.SLEEP_PERIOD):
                    continue
                continue
        except Exception as e:
            self.__die(f"Exception in client event loop: {repr(e)}", e)

    def __onReceiveCallback(self, rawData: bytes):
        data = json.loads(rawData.decode())
        if (act_type := data.get('type')):
            if act_type == "down":
                self.__heldActions[data['actionId']] = True
            elif act_type == "up":
                del self.__heldActions[data['actionId']]
        self.emit(data["type"], self.client, data)

    def __onAllMessage(self, rawData):
        data = json.loads(rawData.decode())
        self.emit(TYPES.allMessage, self.client, data)

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
        if not self.client:
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
        Timer(0, self.__onReceiveCallback, args=[b'{"type":"closePlugin"}']).start()
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
        if stateId and stateId not in self.currentStates or self.currentStates[stateId] != stateValue:
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
        if self.__stopEvent.is_set():
            self.__open()
            self.send({"type":"pair", "id": self.pluginId})
            self.__run()  # start the event loop

    def disconnect(self):
        '''
        This closes the connection to TP and terminates the client processing loop.
        Does nothing if client is already disconnected.
        '''
        if not self.__stopEvent.is_set():
            self.__close()


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
