__copyright__ = """
This file is part of the TouchPortal-API project.
Copyright TouchPortal-API Developers
Copyright (c) 2021 DamienS
All rights reserved.

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

"""
This is another way to create your build config. It's meant to when you import a constants variable
It will hint you on how to create the file.
"""


PLUGIN_MAIN = ""
"""
*REQUIRED*
PLUGIN_MAIN: This lets tppbuild know where your main python plugin file is located so it will know which file to compile.
Note: This can be ether relative or absolute to the main script.
"""

PLUGIN_EXE_NAME = ""
"""
*REQUIRED*
PLUGIN_EXE_NAME: This defines what you want your plugin executable to be named. tppbuild will also use this for the .tpp file in the format:
                `pluginname + "_v" + version + "_" + os_name + ".tpp"`
"""

PLUGIN_EXE_ICON = r""
"""
*OPTIONAL*
PLUGIN_EXE_ICON: This should be a path to a .ico file. However if png is passed in, it will tries to automatically converted to ico. if `PILLOW` is installed.
"""

PLUGIN_ENTRY = ""
"""
*REQUIRED*
PLUGIN_ENTRY: This can be either path to entry.tp or path to a python file that contains infomation about entry.
Note if you pass in a entry.tp, tppbuild will automatically validate the json. If you pass in a python file, it will
build entry.tp & validate it for you. If validation fails, tppbuild will exit.
"""

PLUGIN_ENTRY_INDENT = 2
"""
*OPTIONAL*
This allows you to set indent for the `entry.tp` json data. Default is `2`
but if you want to save space use `-1` meaning no indent. This is only used if `PLUGIN_ENTRY` is a py file.
"""

PLUGIN_ROOT = ""
""" 
*REQUIRED*
This is the root folder name that will be inside of .tpp
 """


PLUGIN_ICON = r""
""" 
*OPTIONAL*
Path to icon file that is used in entry.tp for category `imagepath`, if any.
 If left blank, TP will use a default icon. """

OUTPUT_PATH = r"./"
"""
*OPTIONAL*
This tells tppbuild where you want finished build tpp to be saved at. 
If leaved empty it will store tpp to current dir where this build config is located. 
"""


PLUGIN_VERSION = " "
"""
*OPTIONAL*
A version string will be used as part of .tpp file. example input `PLUGIN_VERSION = "1.0.0-beta1"`
"""

ADDITIONAL_FILES = []
"""
*OPTIONAL*
If you have any required file(s) that your plugin needs, put them in this list.
"""

ADDITIONAL_PYINSTALLER_ARGS = []
"""
*OPTIONAL*
Any additional arguments to be passed to Pyinstaller. Optional.
"""

import sys
import os
import inspect

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import tppbuild

"""
validateBuild() this takes no arguments. when It's called it will check for all
required constants variable are vaild It will check if path is vaild, is a file etc... If 
any error is found, It will list all the error during the process.
"""
def validateBuild():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    constants = module.__dir__()
    os.chdir(os.path.split(module.__file__)[0])

    requiredVar = [
        "PLUGIN_ENTRY", "PLUGIN_MAIN", "PLUGIN_ROOT", "PLUGIN_EXE_NAME"
    ]
    optionalVar = [
        "ADDITIONAL_PYINSTALLER_ARGS", "PLUGIN_ICON", "PLUGIN_EXE_ICON",
        "ADDITIONAL_FILES", "OUTPUT_PATH", "PLUGIN_VERSION", "PLUGIN_ENTRY_INDENT"
    ]
    attri_list = requiredVar + optionalVar

    checklist = [attri in constants for attri in attri_list]
    print("Checking if all constants variable exists")
    if all(checklist) == False:
        print(f"{os.path.basename(module.__file__)} is missing these variables: ", " ".join([attri for attri in attri_list if attri not in dir(constants)]))
        return 0

    print("Checking variable is vaild")

    anyError = False

    if module.PLUGIN_MAIN and not os.path.isfile(module.PLUGIN_MAIN):
        print(f"PLUGIN_MAIN is ether empty or invalid file path.")
        anyError = True

    if module.PLUGIN_ENTRY and not os.path.isfile(module.PLUGIN_ENTRY):
        print(f"PLUGIN_ENTRY is ether empty or invalid file path.")
        anyError = True

    if not module.PLUGIN_ROOT:
        print("PLUGIN_ROOT is empty. Please give a plugin root folder name.")
        anyError = True

    if not module.PLUGIN_EXE_NAME:
        print("PLUGIN_EXE_NAME is empty. Please input a name for plugin's exe")
        anyError = True

    if module.PLUGIN_ICON and not os.path.isfile(module.PLUGIN_ICON) and module.PLUGIN_ICON.endswith(".png"):
        print("PLUGIN_ICON has a value but the value is invaild. It needs a path to a png file.")

    if module.PLUGIN_EXE_ICON and os.path.isfile(module.PLUGIN_EXE_ICON):
        if not module.PLUGIN_EXE_ICON.endswith(".ico"):
            try:
                import PIL
            except ModuleNotFoundError:
                print("PLUGIN_EXE_ICON icon format is not ico and cannot perform auto convert due to missing module. Please install Pillow 'pip install Pillow'")
    else:
        if module.PLUGIN_EXE_ICON:
            print(f"PLUGIN_EXE_ICON is ether empty or invaild path")

    if module.ADDITIONAL_FILES:
        for file in module.ADDITIONAL_FILES:
            if not os.path.isfile(file):
                print("ADDITIONAL_FILES Cannot find", file)
    

    if not anyError:
        print("Validation completed successfully, No error found.")

"""
runBuild() this takes no arguments. This is the same as `tppbuild file.py` you do not need to pass your build config,
It will automatically find it.
"""
def runBuild():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    file = module.__file__

    tppbuild.main([file])