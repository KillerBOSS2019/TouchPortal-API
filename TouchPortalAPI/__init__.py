"""
## Python API and SDK for Touch Portal.

Easy way to build plugins for [Touch Portal](https://touch-portal.com) using Python.

Check the [source repository](https://github.com/KillerBOSS2019/TouchPortal-API/)
for latest version.

## Basic API Usage

More complete example(s) may be found in the code repository's
[examples folder](https://github.com/KillerBOSS2019/TouchPortal-API/tree/main/examples).

```python
import TouchPortalAPI # Import the api

# Initiate the client (replace YourPluginID with your ID)
TPClient = TouchPortalAPI.Client('YourPluginID')

# This event handler will run once when the client connects to TouchPortal
@TPClient.on('info')
def onStart(data):
    # `data` is a Python `dict` object created from de-serialized JSON data sent by TP.
    print('I am Connected!', data)

    # Update a state value in TouchPortal
    TPClient.stateUpdate("(Your State ID)", "State Value")

    # Or create a list with however many states you want and use this method to send them all
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

# Action handlers, called when user activates one of this plugin's actions in Touch Portal.
@TPClient.on('action')
def onActions(data):
    print(data)

# This function gets called every time when someone changes something in your plugin settings
@TPClient.on('settings')
def onSettings(data):
    print('received data from settings!')

# Shutdown handler, called when Touch Portal wants to stop your plugin.
@TPClient.on('closePlugin')
def onShutdown(data):
    print('Received shutdown message!')
    # Terminates the connection and returns from connect()
    TPClient.disconnect()

# Connect to Touch Portal and block (wait) until disconnected
TPClient.connect()
```

"""
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

__version__ = "1.6"  # this is read from setup.py and possibly other places

# maintain backwards compatability
from . client import Client, TYPES
from . tools import Tools
