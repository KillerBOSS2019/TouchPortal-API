# Touch Portal API and SDK for Python
Easy way to build plugins for [Touch Portal](https://touch-portal.com) using Python.

## Installation
The latest release can be found on [PyPi](https://pypi.org/project/TouchPortal-API/). Simply run:

`pip install TouchPortal-API`

Alternatively, download/clone the source code from this repository and either:
- `pip install <path_to_source>`
- `python <path_to_source>/setup.py install`
- or place the `/TouchPortalAPI` folder and its contents from here into your plugin project's folder.

### Requires
- Python v3.8 or higher.
- Additional Python modules `pyee` and `requests` (dependencies are automatically installed during setup, if necessary).
- This Python API supports Touch Portal API version 3.0, as used in Touch Portal V2.3+.
- Some TP API v4 features have been implemented, but have not yet been fully tested, pending release of TP v2.4.


## Documentation

The API and SDK are documented in the code using common Python conventions.

Generated documentation is published at https://KillerBOSS2019.github.io/TouchPortal-API/


## Examples

A working plugin example is included in our repository which demonstrates usage of the API and SDK.
Check the [examples folder](https://github.com/KillerBOSS2019/TouchPortal-API/tree/main/examples).

### Basic Usage Example

Make a folder in `%appdata%/TouchPortal/plugins/` called `ExamplePlugin`
and make a file there called `entry.tp` and paste this JSON data into that file:

```json
{
  "sdk": 3,
  "version": 100,
  "name": "Example Plugin",
  "id": "ExamplePlugin",
  "categories": [
    {
      "id": "Main",
      "name": "Example Plugin",
      "actions": [
        {
          "id": "ExampleAction",
          "name": "This is an Example Action",
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
      "states": [
        {
          "id": "ExampleState",
          "type": "text",
          "desc": "Example State",
          "default": "None"
        }
      ]
    }
  ]
}
```

Restart Touch Portal and you should see your plugin.
Now create a new file named `plugin.py` with the following
Python script. Note that the plugin, action, and state IDs
used in the script correspond to the ones specified in the
`entry.tp` JSON.

```python
import TouchPortalAPI as TP

# Setup callbacks and connection
TPClient = TP.Client("ExamplePlugin")

# This event handler will run once when the client connects to Touch Portal
@TPClient.on(TP.TYPES.onConnect) # Or replace TYPES.onConnect with 'info'
def onStart(data):
    print("Connected!", data)
    # Update a state value in TouchPortal
    TPClient.stateUpdate("ExampleState", "Connected!")

# Action handlers, called when user activates one of this plugin's actions in Touch Portal.
@TPClient.on(TP.TYPES.onAction) # Or 'action'
def onAction(data):
    print(data)
    # do something based on the action ID and the data value
    if data['actionId'] == "ExampleAction":
      # get the value from the action data (a string the user specified)
      action_value = getActionDataValue(data.get('data'), 'ExampleTextData')
      print(action_value)
      # We can also update our ExampleStates with the Action Value
      TPClient.stateUpdate("ExampleStates", action_value)

# Shutdown handler, called when Touch Portal wants to stop your plugin.
@TPClient.on(TP.TYPES.onShutDown) # or 'closePlugin'
def onShutdown(data):
    print("Got Shutdown Message! Shutting Down the Plugin!")
    # Terminates the connection and returns from connect()
    TPClient.disconnect()

# After callback setup like we did then we can connect.
# Note that `connect()` blocks further execution until
# `disconnect()` is called in an event handler, or an
# internal error occurs.
TPClient.connect()
```

You should now be able to run this script from a command line (terminal)
and it will interact with Touch Portal. To try it out, create a new button
on a TP page which uses this plugin's "ExampleAction" action.


## Change Log

```
1.6.3 (5/27/2022)
-------------------
- Added shortId
- sdk_spec updated to support parentGroup and new version of SDK

1.6.2 (1/14/2022)
-------------------
- removed extra _ from connectorUpdate

1.6.1 (1/10/2022)
-------------------
- Fixed connectorUpdate method
  - connectorValue needs to be a string
  - connectorId provided prefix eg "pc_yourpluginid_"

1.6 (8/26/2021)
-------------------
- Notification (https://www.touch-portal.com/api/index.php?section=notifications)
  - Added notificationOptionClicked events to class TYPES
  - Added showNotification() method
- Connector can be used as silder (https://www.touch-portal.com/api/index.php?section=connectors)
  - Added connectorChange events to class TYPES
  - Added connectorUpdate method
- Client and Tools classes can now be imported separately as submodules.
- Added and updated lots of API documentation in code using Python "docstrings."
  - Reference docs now published at https://KillerBOSS2019.github.io/TouchPortal-API/


1.5 (7/28/2021)
-------------------
- Added tppsdk (Allows you to create entry.tp within your code.)

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

## Bugs and Suggestions
Please report any problems using GitHub [Issues](https://github.com/KillerBOSS2019/TouchPortal-API/issues)
and feel free to use the [Discussion](https://github.com/KillerBOSS2019/TouchPortal-API/discussions)
feature as well.

## Contribute
Feel free to suggest a pull request for new features, improvements, or documentation.
If you are not sure how to proceed with something, please start an Issue or Discussion
at the GitHub repository.
