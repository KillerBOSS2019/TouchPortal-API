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
the `TPClient.on()` uses "type" for example "info" `{"type":"pair","id":"(plugin_id)"}` which is from that so you would put `TPClient.on('info')`
You can find more at TouchPortal API doc link should be below

## Full TouchPortal API Doc
https://www.touch-portal.com/api/index.php?section=intro

## Bugs
If theres any bugs, Issues, or need help how to use it feel free use Issue tab

## Contribute
Feel Free to suggest a pull request or Fork
