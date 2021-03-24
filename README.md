# TouchPortal-API for Python
Easy way to Build Plugins for TouchPortal with little understanding of Python.

## Installation
simply run this in your command line `pip install TouchPortal-API` if your not able to you can download [here](https://pypi.org/project/TouchPortal-API/#files) and do `pip install [fileyoudownloaded]`
Make Sure your on latest version of TouchPortal current Version of TouchPortal API supports TP V2.3

## Usage
```python
import TouchPortalAPI # This is how you import the plugin

TPClient = TouchPortalAPI.Client('YourPluginID') # replace "YourPluginID" with your own Pluginid in your entry.tp

@TPClient.on('info')  # This Will run once You've connected to TouchPortal
def OnStart(client, data):
    # You must provide 2 parm in the function or else it will give error 
    print('I am Connected!', data)
    
    
    TPClient.stateUpdate("(Your State ID)", "State Value") # This if you want to update a dymic states in TouchPortal
    
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
    TPClient.stateUpdateMany(updateStates) # Or You can create an list with however many state you want and use this function to send them all
    
@TPClient.on('action')  # This manages when you press a button in TouchPortal it will send here in json format
def Actions(client, data):
    print(data)

@TPClient.on('settingUpdate') # This Function will get called Everytime when someone changes something in your plugin settings
def Settings(client, data):
    print('received data from settings!')
    
@TPClient.on('closePlugin') # When TouchPortal sends close Plugin message it will run this function
def shutDown(client, data):
    print('Received shutdown message!')
    TPClient.disconnect() # This is how you disconnect once you received the closePlugin message
    
    
TPClient.connect() # After you setup everything you need to call this in order to connect to TouchPortal

```


You can also do this
```
import TouchPortalAPI

TPClient = TouchPortalAPI.Client('YourPluginId')

@TPClient.on('message') # This means it will run this on any message come from socket so you dont need to do multiple.
def TPMessage(client, data):
    print(data)

TPClient.connect()
```

There is also some tools that you can use not 2 many atm but here it is
```
from TouchPortal import Tools

Tools.convertImage_to_base64('pathtoyourimage.png') # This can be a url or a image that is stored on your pc if is url just need to pass in the Url

Tools.updateCheck('KillerBOSS2019', 'TP-YTDM-Plugin', 'V1.0') # This only works with github the first parm is your github account and 2nd parm is your plugin  #repository and the 3rd one is the current version that your going to upload it. If there is a update it will return the json data of your repository and If theres #No # updates it will return you False
```

the `TPClient.on()` uses "type" for example "info" `{"type":"pair","id":"(plugin_id)"}` which is from that so you would put `TPClient.on('info')`
and there is another class in this API which is called TYPES it has all the types (atleast i think so) you can access it by doing
- TYPES.onHold_up  - "up"
- TYPES.onHold_down  - "down"
- TYPES.onConnect  - "info"
- TYPES.onAction  - "action"
- TYPES.onListChange  - "listChange"
- TYPES.onShutdown  - "closePlugin"
- TYPES.onBroadcast  - "broadcast"
- TYPES.onSettingUpdate  - "settings"
- TYPES.allMessage  - "message" # This one is not build in to TouchPortal it's a custom one that it send any message from TP

## Full TouchPortal API Doc
https://www.touch-portal.com/api/index.php?section=intro

## Bugs
If theres any bugs, Issues, or need help how to use it feel free use Issue tab

## Contribute
Feel Free to suggest a pull request or Fork
