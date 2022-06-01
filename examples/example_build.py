
# first, some values which may be used in multiple places below

# directory for plugin source code
pluginSourcePath = "./"
# the base file name for the plugin's main file, w/out .py extension
pluginFileName = "plugin-example"

"""
PLUGIN_MAIN: This lets tppbuild know where your main python plugin file is located so it will know which file to compile.
"""
PLUGIN_MAIN = pluginSourcePath + pluginFileName + ".py"

"""
PLUGIN_EXE_NAME: This defines what you want your plugin executable to be named. tppbuild will also use this for the .tpp file in the format:
                `pluginname + "_v" + version + "_" + os_name + ".tpp"`
                If left blank, the file name from PLUGIN_MAIN is used (w/out .py extension).
"""
PLUGIN_EXE_NAME = "pluginexample"

"""
PLUGIN_EXE_ICON: This should be a path to a .ico file that's used for the compiled exe (If left empty, the default pyinstaller icon will be used)
"""
PLUGIN_EXE_ICON = r""


"""
PLUGIN_ENTRY: This can be either path to entry.tp or path to a python file that contains infomation about entry.
Note if you pass in a entry.tp, tppbuild will automatically validate the json. If you pass in a python file, it will
build entry.tp & validate it for you.
"""
PLUGIN_ENTRY = PLUGIN_MAIN  # Here we just use the same file as the plugin's main code since that contains all the definitions for entry.tp.

""" This is the root folder name that will be inside of .tpp """
PLUGIN_ROOT = "TPExamplePlugin"

""" Path to icon file used in entry.tp for category `imagepath`, if any. If left blank, TP will use a default icon. """
PLUGIN_ICON = r"icon-24.png"

""" This tells tppbuild where you want finished build tpp to be saved at. Default "./" meaning current dir where tppbuild is running from. """
OUTPUT_PATH = r"./"

""" PLUGIN_VERSION: A version string for the generated .tpp file name. This example reads the `__version__` from the example plugin's code. """
import importlib
from sys import path
path.insert(1, pluginSourcePath)
plugin = importlib.import_module(pluginFileName)
PLUGIN_VERSION = plugin.__version__

# Or just set the PLUGIN_VERSION manually.
# PLUGIN_VERSION = "1.0.0-beta1"

"""
If you have any required file(s) that your plugin needs, put them in this list.
"""
FileRequired = []

"""
Any additional arguments to be passed to Pyinstaller. Optional.
"""
Pyinstaller_arg = []

