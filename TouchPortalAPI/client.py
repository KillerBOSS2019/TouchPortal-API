__copyright__ = """
    This file is part of the TouchPortal-API project.
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
from concurrent.futures import Executor, ThreadPoolExecutor
from threading import Event, Lock

__all__ = ['Client', 'TYPES']

class TYPES:
    """
    Event type enumerations. These correspond to the message types Touch Portal may send.
    Event handler callbacks receive one parameter, which is the JSON data structure sent
    from TP and then converted to a corresponding Python object using `json.loads()`.
    Usage example:
        ```py
        import TouchPortalAPI as TP

        client = TP.Client("myplugin")

        @client.on(TP.TYPES.onConnect)
        # equivalent to: @client.on('info')
        def onConnect(data):
            print(data)

        # alternatively, w/out decorators:
        def onAction(data):
            print(data)

        client.on(TP.TYPES.onAction, onAction)
        ```
    """
    onHold_up = 'up'
    """ When the action is used in a hold functionality and the user releases the Touch Portal button (Api 3.0+) """
    onHold_down = 'down'
    """ When the action is used in a hold functionality and the user presses the Touch Portal button down (Api 3.0+) """
    onConnect = 'info'
    """ Info message returned after successful pairing. """
    onAction = 'action'
    """ When actions are triggered by the user (Api 1.0+) """
    onListChange = 'listChange'
    """ When a user makes a change in one of your lists (Api 1.0+) """
    onConnectorChange = 'connectorChange'
    """ When a connector is used in a slider functionality (connector) (Api 4.0+) """
    onShutdown = 'closePlugin'
    """ When Touch Portal tries to close your plug-in (Api 2.0+) """
    onBroadcast = 'broadcast'
    """ When Touch Portal broadcasts a message (Api 3.0+) """
    onSettingUpdate = 'settings'
    """ When the plugin's Settings have been updated (by user or from the plugin itself) (Api 3.0+) """
    onNotificationOptionClicked = "notificationOptionClicked"
    """ When a user clicks on a notification action (Api 4.0+) """
    allMessage = 'any'
    """ Special event handler which will receive **all** messages from TouchPortal. """
    onError = 'error'
    """ Special event emitted when any other event callback raises an exception.
        For this particular event, the parameter passed to the callback handler will be an `Exception` object.
        See also `pyee.ExecutorEventEmitter.error` event.
    """

class Client(ExecutorEventEmitter):
    """
    A TCP/IP client for [Touch Portal API](https://www.touch-portal.com/api) plugin integration.
    Implements a [pyee.ExecutorEventEmitter](https://pyee.readthedocs.io/en/latest/#pyee.ExecutorEventEmitter).

    After an initial connection to a Touch Portal desktop application "server," the client
    implements a send/receive event loop while maintaining the open sockets. Messages between
    TP and the plugin are exchanged asynchronously, with all sending methods possibly returning
    before the actual data is sent.

    Messages from Touch Portal are delivered to the plugin script via event handler callbacks,
    which can be either individual callbacks per message type, and/or a single handler for all
    types of messages. The callbacks are executed in separate Thread(s), using a pool of up to
    any number of concurrent threads as needed (if using more than one thread, the plugin
    code itself is responsible for thread safety of its internal data). Please check the
    `pyee.EventEmitter` documentation for general information on how events are handled
    (which can be either via function decorators or via the inherited `Client.on()` method).

    Generated event names correspond to Touch Portal API message types, one for each type
    as defined in the TP API documentation (eg. "action" or "listChange") as well as one event
    which is generated for all message types ("any"). Alternately, for a more formal approach,
    the corresponding members of the `TYPES` class could be used instead of string names
    (eg. `TYPES.onAction` or `TYPES.onListChange`).

    Any errors raised within event listeners/handlers are trapped and then reported in the
    inherited "error" event (from pyee.ExecutorEventEmitter), aka `TYPES.onError`.
    """
    TPHOST = '127.0.0.1'
    """ TP plugin server host IPv4 address. """
    TPPORT = 12136
    """ TP plugin server host IPv4 port number. """
    RCV_BUFFER_SZ = 4096
    """ [B] incoming data buffer size. """
    SND_BUFFER_SZ = 32**4
    """ [B] maximum size of send data buffer (1MB). """
    SOCK_EVENT_TO = 1.0
    """ [s] maximum wait time for socket events (blocking timeout for selector.select()). """

    def __init__(self, pluginId:str,
                 sleepPeriod:float = 0.01,
                 autoClose:bool = False,
                 checkPluginId:bool = True,
                 updateStatesOnBroadcast:bool = True,
                 maxWorkers:int = None,
                 executor:Executor = None):
        """
        Creates an instance of the client.

        Args:
            `pluginId`: ID string of the TouchPortal plugin using this client. **Required.**
            `sleepPeriod`: Seconds to sleep the event loop between socket read events. Default: 0.01
            `autoClose`: If `True` then this client will automatically disconnect when a `closePlugin` message is received from TP.
                Default is `False`.
            `checkPluginId`: Validate that `pluginId` matches ours in any messages from TP which contain one (such as actions).
                Default is `True`.
            `updateStatesOnBroadcast`: Re-send all cached State values whenever user switches TP page.
                Default is `True`.
            `maxWorkers`: Maximum worker threads to run concurrently for event handlers.
                Default of `None` creates a default-constructed `ThreadPoolExecutor`.
            `executor`: Passed to `pyee.ExecutorEventEmitter`. By default this is a default-constructed
                [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor),
                optionally using `maxWorkers` concurrent threads.
        """
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
        """
        Returns `True` if the Client is connected to Touch Portal, `False` otherwise.
        """
        return not self.__stopEvent.is_set()

    def isActionBeingHeld(self, actionId:str):
        """
        For an Action with ID of `actionId` that can be held (`hasHoldFunctionality` is true),
        this method returns `True` while it is being held and `False` otherwise.
        """
        return actionId in self.__heldActions

    def createState(self, stateId:str, description:str, value:str):
        """
        This will create a TP State at runtime. `stateId`, `description`, and `value` are all required (`value` becomes the State's default value).
        """
        if stateId and description and value != None:
            if stateId not in self.currentStates:
                self.send({"type": "createState", "id": stateId, "desc": description, "defaultValue": value})
                self.currentStates[stateId] = value
            else:
                self.stateUpdate(stateId, value)

    def createStateMany(self, states:list):
        """
        Convenience function to create several States at once. `states` should be an iteratable of `dict` types
        in the form of `{'id': "StateId", 'desc': "Description", 'value': "Default Value"}`.
        """
        try:
            for state in states:
                if isinstance(state, dict):
                    self.createState(state.get('id', ""), state.get('desc', ""), state.get('value', ""))
                else:
                    raise TypeError(f'createStateMany() requires a list of dicts, got {type(state)} instead.')
        except:
            raise TypeError(f'createStateMany() requires an iteratable, got {type(states)} instead.')

    def removeState(self, stateId:str, validateExists = True):
        """
        This removes a State that has been created at runtime. `stateId` is the ID to remove.
        If `validateExists` is True (default) this method will raise an Exception if the `stateId`
        does not exist in the current state cache.
        """
        if stateId and stateId in self.currentStates:
            self.send({"type": "removeState", "id": stateId})
            self.currentStates.pop(stateId)
        elif validateExists:
            raise Exception(f"{stateId} Does not exist.")

    def removeStateMany(self, states:list):
        """
        Convenience function to remove several States at once. `states` should be an iteratable of state ID strings.
        This method does not validate if the states exist in the current state cache. See also: `removeState`.
        """
        try:
            for state in states:
                self.removeState(state, False)
        except TypeError:
            raise TypeError(f'removeStateMany() requires an iteratable, got {type(states)} instead.')

    def choiceUpdate(self, choiceId:str, values:list):
        """
        This updates the list of choices in a previously-declared TP State with id `stateId`.
        See TP API reference for details on updating list values.
        """
        if choiceId:
            if isinstance(values, list):
                self.send({"type": "choiceUpdate", "id": choiceId, "value": values})
            else:
                raise TypeError(f'choiceUpdate() values argument needs to be a list not a {type(values)}')

    def choiceUpdateSpecific(self, stateId:str, values:list, instanceId:str):
        """
        This updates a list of choices in a specific TP Item Instance, specified in `instanceId`.
        See TP API reference for details on updating specific instances.
        """
        if stateId and instanceId:
            if isinstance(values, list):
                self.send({"type": "choiceUpdate", "id": stateId, "instanceId": instanceId, "value": values})
            else:
                raise TypeError(f'choiceUpdateSpecific() values argument needs to be a list not a {type(values)}')

    def settingUpdate(self, settingName:str, settingValue):
        """
        This updates a value named `settingName` in your plugin's Settings to `settingValue`.
        """
        if settingName and settingName not in self.currentSettings or self.currentSettings[settingName] != settingValue:
            self.send({"type": "settingUpdate", "name": settingName, "value": settingValue})
            self.currentSettings[settingName] = settingValue

    def stateUpdate(self, stateId:str, stateValue:str):
        """
        This updates a value in ether a pre-defined static State or a dynamic State created in runtime.
        """
        self.__stateUpdate(stateId, stateValue, False)

    def __stateUpdate(self, stateId:str, stateValue:str, forced:bool):
        if stateId:
            if forced or stateId not in self.currentStates or self.currentStates[stateId] != stateValue:
                self.send({"type": "stateUpdate", "id": stateId, "value": stateValue})
            self.currentStates[stateId] = stateValue

    def stateUpdateMany(self, states:list):
        """
        Convenience function to update several states at once.
        `states` should be an iteratable of `dict` types in the form of `{'id': "StateId", 'value': "The New Value"}`.
        """
        try:
            for state in states:
                if isinstance(state, dict):
                    self.stateUpdate(state.get('id', ""), state.get('value', ""))
                else:
                    raise TypeError(f'StateUpdateMany() requires a list of dicts, got {type(state)} instead.')
        except TypeError:
            raise TypeError(f'StateUpdateMany() requires an iteratable, got {type(states)} instead.')

    def showNotification(self, notificationId:str, title:str, msg:str, options:list):
        """
        This method allows your plugin to send a notification to Touch Portal with custom title, message body and available user action(s).
        Requires TP SDK v4.0 or higher.

        Args:
            `notificationId`: Unique ID of this notification.
            `title`: The notification title.
            `msg`: The message body text that is shown in the notifcation.
            `options`: List of options (actions) for the notification. Each option should be a `dict` type with `id` and `title` keys.
        """
        if notificationId and title and msg and options and isinstance(options, list):
            for option in options:
                if 'id' not in option.keys() or 'title' not in option.keys():
                    raise TypeError("all options require id and title keys")
            self.send({
                "type": "showNotification",
                "notificationId": str(notificationId),
                "title": str(title),
                "msg": str(msg),
                "options": options
            })

    def connectorUpdate(self, connectorId:str, connectorValue:int):
        """
        This allows you to update slider position value.

        Args:
            `connectorId`: Cannot be longer then 200 characters.
                connectorId have syntax that you need to follow https://www.touch-portal.com/api/index.php?section=connectors
                Also according to that site It requires you to have prefix "pc_yourPluginId_" + connectorid however This already provide
                you the prefix and the pluginId so you just need you take care the rest eg connectorid|setting1=aValue
            `connectorValue`: Must be an integer between 0-100.
        """
        if not isinstance(connectorId, str):
            raise TypeError(f"connectorId needs to be a str not a {type(connectorId)}")
        if not isinstance(connectorValue, int):
            raise TypeError(f"connectorValue requires a int not {type(connectorValue)}")
        if 0 <= connectorValue <= 100:
            self.send({
                "type": "connectorUpdate",
                "connectorId": f"pc_{self.pluginId}_{connectorId}_",
                "value": str(connectorValue)
            })
        else:
            raise TypeError(f"connectorValue needs to be between 0-100 not {connectorValue}")

    def updateActionData(self, instanceId:str, stateId:str, minValue, maxValue):
        """
        This allows you to update Action Data in one of your Action. Currently TouchPortal only supports changing the minimum and maximum values in numeric data types.
        """
        self.send({"type": "updateActionData", "instanceId": instanceId, "data": {"minValue": minValue, "maxValue": maxValue, "id": stateId, "type": "number"}})

    def send(self, data):
        """
        This will try to send any arbitrary Python object in `data` (presumably something `dict`-like) to Touch Portal
        after serializing it as JSON and adding a `\n`. Normally there is no need to use this method directly, but if the
        Python API doesn't cover something from the TP API, this could be used instead.
        """
        if self.__getWriteLock():
            if len(self.__sendBuffer) + len(data) > self.SND_BUFFER_SZ:
                self.__writeLock.release()
                raise ResourceWarning("TP Client send buffer is full!")
            self.__sendBuffer += (json.dumps(data)+'\n').encode()
            self.__writeLock.release()
            self.__dataReadyEvent.set()

    def connect(self):
        """
        Initiate connection to TP Server.
        If successful, it starts the main processing loop of this client.
        Does nothing if client is already connected.

        **Note** that `connect()` blocks further execution of your script until one of the following occurs:
          - `disconnect()` is called in an event handler,
          - TP sends `closePlugin` message and `autoClose` is `True`
          - or an internal error occurs (for example Touch Portal disconnects unexpectedly)
        """
        if not self.isConnected():
            self.__open()
            self.send({"type":"pair", "id": self.pluginId})
            self.__run()  # start the event loop

    def disconnect(self):
        """
        This closes the connection to TP and terminates the client processing loop.
        Does nothing if client is already disconnected.
        """
        if self.isConnected():
            self.__close()

    @staticmethod
    def getActionDataValue(data:list, valueId:str=None):
        """
        Utility for processing action messages from TP. For example:
            {"type": "action", "data": [{ "id": "data object id", "value": "user specified value" }, ...]}

        Returns the `value` with specific `id` from a list of action data,
        or `None` if the `id` wasn't found. If a null id is passed in `valueId`
        then the first entry which has a `value` key, if any, will be returned.

        Args:
            `data`: the "data" array from a TP "action", "on", or "off" message
            `valueId`: the "id" to look for in `data`. `None` or blank to return the first value found.
        """
        if not data: return None
        if valueId:
            return next((x.get('value') for x in data if x.get('id', '') == valueId), None)
        return next((x.get('value') for x in data if x.get('value') != None), None)
