# [TouchPortal](https://touch-portal.com)-API for Python
Easy way to Build Plugins for TouchPortal with little understanding of Python.

## Installation
Simply run this in your command line `pip install TouchPortal-API`. Or you can download
[here](https://pypi.org/project/TouchPortal-API/#files) and do `pip install [fileyoudownloaded]`.
Or, download/clone the source code from this repository and place the `TouchPortalAPI/TouchPortalAPI` folder
from here into your plugin project's folder.

Make sure to use the latest version of Touch Portal. This Python API supports Touch Portal API version 3.0, as used in TP V2.3+.

## Usage
```python
import TouchPortalAPI # Import the api

# Initiate the client (replace YourPluginID with your ID)
TPClient = TouchPortalAPI.Client('YourPluginID')

# This Will run once You've connected to TouchPortal
@TPClient.on('info')
def OnStart(data):
    # `data` is a Python `dict` object created from de-serialized JSON data sent by TP.
    print('I am Connected!', data)

    # This if you want to update a dynamic states in TouchPortal
    TPClient.stateUpdate("(Your State ID)", "State Value")

    # Or You can create an list with however many state you want and use this function to send them all
    updateStates = [
        {
            "id": "(Your State ID)",
            "value": "(The Value You wanted)"
        },
        {
            "id": "(Your 2nd State ID)",
            "value": "(The Value You wanted)"
        }
    ]
    TPClient.stateUpdateMany(updateStates)

# This manages when you press a button in TouchPortal it will send here in json format
@TPClient.on('action')
def Actions(data):
    print(data)

# This Function will get called every time when someone changes something in your plugin settings
@TPClient.on('settings')
def Settings(data):
    print('received data from settings!')

# When TouchPortal sends close Plugin message it will run this function
@TPClient.on('closePlugin')
def shutDown(data):
    print('Received shutdown message!')
    TPClient.disconnect() # This is how you disconnect once you received the closePlugin message


TPClient.connect() # Connect to Touch Portal
```

## Example Plugin
Make a Folder in `%appdata%/TouchPortal/plugins/` called `ExamplePlugin`
and make a file called entry.tp and paste this json data inside.
```json
{
  "sdk": 3,
  "version": 100,
  "name": "Example Plugin",
  "id": "ExamplePlugin",
  "configuration": {
    "colorDark": "#222423",
    "colorLight": "#020202"
  },
  "categories": [
    {
      "id": "Main",
      "name": "Example Plugin",
      "actions": [
	{
	  "id": "ExampleAction",
	  "name": "This is Example Action",
	  "prefix": "plugin",
	  "type": "communicate",
	  "tryInline": true,
	  "format": "Print({$ExampleTextData$})",
	  "data": [
		  {
		    "id": "ExampleTextData",
	      "type": "text",
	      "label": "text",
	      "default": "Hello World"
			}
		 ]
	      }
      ],
      "events": [],
      "states": [
	      {
	  "id": "ExampleStates",
	  "type": "text",
	  "desc": "Example States",
	  "default": "None"
	}
      ]
    }
  ]
}
```

Save this somewhere and also Make sure you've Setup the entry.tp file as well then reboot TouchPortal
you should see your plugin. Without This script the Plugin wont do anything right? lets run this file
and Use one of the action! Note This is just a Example Plugin
```python
import TouchPortalAPI as TP

# Setup callbacks and connection
TPClient = TP.Client("ExamplePlugin")

@TPClient.on(TP.TYPES.onConnect) # Or replace TYPES.onConnect with 'info'
def onStart(data):
    print("Connected!", data)

@TPClient.on(TP.TYPES.onAction) # Or 'action'
def Actions(data):
    print(data)
    # do something based on the action ID and the data value
    if data['actionId'] == "ExampleAction":
    # get the value from the action data (a string the user specified)
    action_value = getActionDataValue(data, 'ExampleTextData')
    print(action_value)
    # We can also update our ExampleStates with the Action Value
    TPClient.stateUpdate("ExampleStates", action_value)

@TPClient.on(TP.TYPES.onShutDown) # or 'closePlugin'
def shutDown(data):
    print("Got Shutdown Message! Shutting Down the Plugin!")
    TPClient.disconnect() # This stops the connection to TouchPortal

# After Callback setup like we did then we can connect
# Note that `connect()` blocks further execution until
# `disconnect()` is called in an event handler, or an
# internal error occurs.
TPClient.connect()
```

## API Documentation

### `TouchPortalAPI.TYPES`
- `onHold_up`  - "up"
- `onHold_down`  - "down"
- `onConnect`  - "info"
- `onAction`  - "action"
- `onListChange`  - "listChange"
- `onShutdown`  - "closePlugin"
- `onBroadcast`  - "broadcast"
- `onSettingUpdate`  - "settings"
- `allMessage`  - "message"
  - Special event handler which will receive **all** messages from TouchPortal.
- `onError` - "error"
  - Special event emitted when any other event callback raises an exception. For this particular event, the parameter
  passed to the callback handler will be an `Exception` object. See also `pyee.ExecutorEventEmitter.error` event.


### `TouchPortalAPI.Client()`
  A client for TouchPortal plugin integration using event listener callbacks.
  Implements a [pyee.ExecutorEventEmitter](https://pyee.readthedocs.io/en/latest/#pyee.ExecutorEventEmitter).

  Arguments:
  - `pluginId`       (str): ID string of the TouchPortal plugin using this client. **Required**.
  - `sleepPeriod`  (float): Seconds to sleep the event loop between socket read events (default: 0.01).
  - `autoClose`     (bool): If `True` then this client will automatically disconnect when a `closePlugin` message is received from TP.
  - `updateStatesOnBroadcast` (bool): Default `True` Which means when user switch page It will auto update all the states to get fresh data.
  - `checkPluginId` (bool): Validate that `pluginId` matches ours in any messages from TP which contain one (such as actions). Default is `True`.
  - `maxWorkers`     (int): Maximum worker threads to run concurrently for event handlers. Default of `None` creates a default-constructed `ThreadPoolExecutor`.
  - `executor`    (object): Passed to `pyee.ExecutorEventEmitter`. By default this is a default-constructed
                          [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor),
                          optionally using `maxWorkers` concurrent threads.


#### List of Methods
- `isActionBeingHeld(actionId)`
  - This returns `True` or `False` for an Action ID. If you have an Action that can be held, this nethod would return `True` while it is being held, and `False` otherwise.
- `createState(stateId, description, value)`
  - This will create a TP State at runtime. `stateId`, `description`, and `value` are all required (`value` becomes the State's default value).
  If the State already exists, it will be updated with `value` instead of being re-created.
- `createStateMany(stateId, states:list)`
  - Convenience function to create several States at once. `states` should be an iteratable of `dict` types in the form of `{'id': "StateId", 'desc': "Description", 'value': "Default Value"}`.
- `removeState(stateId)`
  - This removes a State that has been created at runtime. `stateId` needs to be a string.
- `removeStateMany(states)`
  - Convenience function to remove several States at once. `states` should be an iteratable of state ID strings.
- `choiceUpdate(stateId, values)`
  - This updates the list of choices in a previously-declared TP State with id `stateId`. See TP API reference for details on updating list values.
- `choiceUpdateSpecific(stateId, values, instanceId)`
  - This updates a list of choices in a specific TP Item Instance, specified in `instanceId`. See TP API reference for details on updating specific instances.
- `settingUpdate(settingName, settingValue)`
  - This updates a value in your plugin's Settings.
- `stateUpdate(stateId, stateValue)`
  - This updates a value in ether a pre-defined static State or a dynamic State created in runtime.
- `stateUpdateMany(states)`
  - Convenience function to update serveral states at once. `states` should be an iteratable of `dict` types in the form of `{'id': "StateId", 'value': "The New Value"}`.
- `updateActionData(instanceId, stateId, minValue, maxValue)`
  - This allows you to update Action Data in one of your Action. Currently TouchPortal only supports changing the minimum and maximum values in numeric data types.
- `send(data)`
  - This will try to send any arbitrary Python object in `data` (presumably something `dict`-like) to TouchPortal
  after serializing it as JSON and adding a `\n`. Normally there is no need to use this method directly, but if the
  Python API doesn't cover something from the TP API, this could be used instead.
- `connect()`
  - Call this method to connect to TouchPortal after all your setups are complete. Normally this is used at the end of
  your script.  Does nothing if the client is already connected.
  - If connection is successful, it starts the main processing loop of the TP network client.
  - **Note** that `connect()` blocks further execution of your script until `disconnect()` is called in an event handler,
  (when `autoClose` is `False`), TP sends `closePlugin` message and `autoClose` is `True`, or an internal error occurs
  (for example Touch Portal disconnects unexpectedly).
- `disconnect()`
  - Trigger the client to disconnect from TouchPortal. Normally this is used in `@TPClient.on("closePlugin")`
  callback but it can be used any way you like. Does nothing if client is not currently connected.
  - It is not necessary to call this method if `autoClose` was set to `True` in the `Client()` constructor.
- `getActionDataValue(data:list, valueId:str=None)`
  - Utility for processing action messages from TP. For example:<br/>
      `{"type": "action", "data": [{ "id": "data object id", "value": "user specified value" }, ...]}`

  - Returns the `value` with specific `id` from a list of action data,
  or `None` if the `id` wasn't found. If a null id is passed in `valueId`
  then the first entry which has a `value` key, if any, will be returned.

  - Arguments:
    - `data`: the "data" array from a TP "action", "on", or "off" message
    - `valueId`: the "id" to look for in `data`. `None` or blank to return the first value found.


### `TouchPortalAPI.Tools`
- `convertImage_to_base64(image, type="Auto", image_formats=["image/png", "image/jpeg", "image/jpg"])`
  - `image` can be a URL or local file path.
  - `type` can be "Auto", "Web" (for URL), or "Local" (for file path).
  - `image_formats` is a list of one or more MIME types to accept, used only with URLs to confirm the response is valid.
  - May raise a `TypeError` if URL request returns an invalid MIME type.
  - May raise a `ValueError` in other cases such as invalid URL or file path.
- `updateCheck(name, repository)`
  - Returns the newest tag name from a GitHub repository.
  - `name` is the GitHub user name for the URL path.
  - `repository` is the GitHub repository name for the URL path.
  - May raise a `ValueError` if the repository URL can't be reached, doesn't exist, or doesn't have any tags.

### Change Log
==========
```
1.4 (7/12/2021)
-------------------
- Removed Socket Object from callback (v1.3 or older required to remove `client` from callback.)
- Added updateStatesOnBroadcast (automatically send all states on Broadcast message.)

1.3 (6/12/2021)
-------------------
Pull requests from [#5](https://github.com/KillerBOSS2019/TouchPortal-API/pull/5) and [#6](https://github.com/KillerBOSS2019/TouchPortal-API/pull/6)
- Minor cleanups
- Refactor Client to use selectors and non-blocking sockets.
- Sync __init__.py with PyPi version.
- Optimize validations and key safety
- Added createStateMany()
- Added removeStateMany()

1.2 (4/12/2021)
-------------------
- Added isActionBeingHeld(actionId) returns True or False

1.1.1 (3/24/2021)
-------------------
Fixes

Fix: fixed the readme for typo's
Fix: keywords
Fix: updateStates now only updates when value changed
Fix: createState now update the state if it already exists
Fix: updateSetting now only updates when value has changed

1.1.0 (3/23/2021)
-------------------
- Fixed some typos

1.0 (3/23/2021)
-------------------
# Feautres
- Easy to use
- createState
- removeState
- choice Update
- choice Update Specific
- setting Update
- state Update
- State Update Many
- Converting image to base64
- Update check
```

## Touch Portal API documentation
https://www.touch-portal.com/api

## Bugs
If theres are any bugs, Issues or if you need help feel free use Issue tab

## Contribute
Feel Free to suggest a pull request or Fork
