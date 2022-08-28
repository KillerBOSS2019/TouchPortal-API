""" 
# TouchPortal Python TPP build tool

## Features

This SDK tools makes compile, packaging and distribution of your plugin easier.

These are the steps the tppbuild will do for you:
- Generate entry.tp if you passed in .py file otherwise it will validate the .tp file and raise an error if it's not valid.
- Compile your main script for your system (Windows, MacOS) depending on the platform you're running on.
- Create a .tpp file with all the files include compiled script, (generated or existing) entry.tp file.
- Also the .tpp file will be renamed into this format pluginname_version_os.tpp

Note that running this script requires `pyinstaller` to be installed. You can install it by running `pip install pyinstaller` in your terminal.

Using it in [example](https://github.com/KillerBOSS2019/TouchPortal-API/tree/main/examples)

```
tppbuild --target example_build.py
```
In this example we targed the example_build.py file because that file contains infomations on how to build the plugin.

## Command-line Usage
The script command is `tppbuild` when the TouchPortalAPI is installed (via pip or setup), or `tppbuild.py` when run directly from this source.

```
<script-command> [-h] <target>

Script to automatically compile a Python plugin into a standalone exe, generate entry.tp, and package them into
importable tpp file.

positional arguments:
  <target>    A build script that contains some infomations about the plugin. Using given infomation about the plugin,
              this script will automatically build entry.tp (if given file is .py) and it will build the distro based
              on which operating system you're using.

options:
  -h, --help  show this help message and exit
```
"""

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

__all__ = ['PLUGIN_MAIN', 'PLUGIN_EXE_NAME', 'PLUGIN_EXE_ICON', 'PLUGIN_ENTRY', 'PLUGIN_ENTRY_INDENT', 'PLUGIN_ROOT',
 'PLUGIN_ICON', 'OUTPUT_PATH', 'PLUGIN_VERSION', 'ADDITIONAL_FILES', 'ADDITIONAL_PYINSTALLER_ARGS', 'ADDITIONAL_TPPSDK_ARGS',
 'validateBuild', 'runBuild']

import importlib
import os
import sys
from zipfile import (ZipFile, ZIP_DEFLATED)
from argparse import ArgumentParser
from glob import glob
from shutil import rmtree
from pathlib import Path
try:
	import PyInstaller.__main__
except ImportError:
	print("PyInstaller is not installed. Please install it before running this script.")
	sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import sdk_tools

def getInfoFromBuildScript(script:str):
	try:
		sys.path.insert(1, os.getcwd()) # This allows build config to import stuff
		spec = importlib.util.spec_from_file_location("buildScript", script)
		buildScript = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(buildScript)
	except Exception as e:
		raise ImportError(f"ERROR while trying to import plugin code from '{script}': {repr(e)}")
	return buildScript

def build_tpp(zip_name, tpp_pack_list):
	print("Creating archive: " + zip_name)
	with ZipFile(zip_name, "w", ZIP_DEFLATED) as zf:
		for src, dest in tpp_pack_list.items():
			zf.write(src, dest + os.path.basename(src))
	print("")

def zip_dir(zf, path, base_path="./", recurse=True):
	relroot = os.path.abspath(os.path.join(path, os.pardir))
	for root, _, files in os.walk(path):
		for file in files:
			src = os.path.join(root, file)
			if os.path.isfile(src):
				dst = os.path.join(base_path, os.path.relpath(root, relroot), file)
				zf.write(src, dst)
			elif recurse and os.path.isdir(src):
				zip_dir(zf, src, base_path)

def build_distro(opsys, version, pluginname, packingList, output):
	if opsys == OS_WIN:
		os_name = "Windows"
	elif opsys == OS_MAC:
		os_name = "MacOS"
	elif opsys == OS_LINUX:
		os_name = "Linux"
	else:
		raise ValueError("Unknown OS")
	zip_name = pluginname + "_v" + str(version) + "_" + os_name + ".tpp"
	print("Creating archive: "+ zip_name)
	if not os.path.exists(output):
		os.makedirs(output)
	with ZipFile(os.path.join(output, zip_name), "w", ZIP_DEFLATED) as zf:
		for src, dest in packingList.items():
			if os.path.isdir(src):
				zip_dir(zf, src, dest)
			elif os.path.isfile(src):
				zf.write(src, dest + os.path.basename(src))

	print("")

def build_clean(distPath, dirPath=None):
	print("Cleaning up...")
	files = glob(distPath)
	files.extend(glob("__pycache__"))

	for file in files:
		if os.path.exists(file):
			print("removing: " + file)
			if os.path.isfile(file):
				os.remove(file)
			elif os.path.isdir(file):
				rmtree(file)
	print("")

def filePath(*file):
	fullpath = os.path.join(*file)
	return str(Path(fullpath).resolve())

		

EXE_SFX = ".exe" if sys.platform == "win32" else ""

OS_WIN = 1
OS_MAC = 2
OS_LINUX = 3

requiredVar = [
        "PLUGIN_ENTRY", "PLUGIN_MAIN", "PLUGIN_ROOT", "PLUGIN_EXE_NAME"
    ]
optionalVar = [
	"ADDITIONAL_PYINSTALLER_ARGS", "PLUGIN_ICON", "PLUGIN_EXE_ICON",
	"ADDITIONAL_FILES", "OUTPUT_PATH", "PLUGIN_VERSION", "PLUGIN_ENTRY_INDENT",
	"ADDITIONAL_TPPSDK_ARGS"
]
attri_list = requiredVar + optionalVar

def main(buildArgs=None):
	if sys.platform == "win32":
		opsys = OS_WIN
	elif sys.platform == "darwin":
		opsys = OS_MAC
	elif sys.platform == "linux":
		opsys = OS_LINUX
	else:
		return "Unsupported OS: " + sys.platform

	parser = ArgumentParser(description=
		"Script to automatically compile a Python plugin into a standalone exe, generate entry.tp, and package them into importable tpp file."
	)

	parser.add_argument(
		"target", metavar='<target>', type=str,
		help='A build script that contains some infomations about the plugin. ' +
		'Using given infomation about the plugin, this script will automatically build entry.tp (if given file is .py) and it will build the distro ' +
		'based on which operating system you\'re using.'
	)

	opts = parser.parse_args(buildArgs)
	del parser

	out_dir = os.path.dirname(opts.target)

	if out_dir:
		os.chdir(out_dir)

	print("tppbuild started with target: " + opts.target)
	buildfile = getInfoFromBuildScript(os.path.basename(opts.target))

	checklist = [attri in dir(buildfile) for attri in attri_list]
	if all(checklist) == False:
		print(f"{opts.target} is missing these variables: ", " ".join([attri for attri in attri_list if attri not in dir(buildfile)]))
		return -1

	TPP_PACK_LIST = {}

	print(f"Building {buildfile.PLUGIN_EXE_NAME} v{buildfile.PLUGIN_VERSION} target(s) on {sys.platform}\n")

	#buildfiledir = filePath(out_dir)

	if os.path.exists(dirPath := os.path.join(buildfile.OUTPUT_PATH, "dist")):
		rmtree(dirPath)
	os.makedirs(dirPath)

	distdir = os.path.join(buildfile.OUTPUT_PATH, 'dist')

	if (entry_abs_path := buildfile.PLUGIN_ENTRY) and os.path.isfile(entry_abs_path):
		sys.path.append(os.path.dirname(os.path.realpath(entry_abs_path)))
		entry_output_path = os.path.join(distdir, "entry.tp")
		if buildfile.PLUGIN_ENTRY.endswith(".py"):
			sdk_arg = [entry_abs_path, f"-i={buildfile.PLUGIN_ENTRY_INDENT}", f"-o={entry_output_path}"]
			sdk_arg.extend(buildfile.ADDITINAL_TPPSDK_ARGS)
		else:
			sdk_arg = [entry_abs_path, "-v"]
			entry_output_path = buildfile.PLUGIN_ENTRY

		result = sdk_tools.main(sdk_arg)
		if result == 0:
			print("Adding entry.tp to packing list.")
			TPP_PACK_LIST[entry_output_path] = buildfile.PLUGIN_ROOT + "/"
		else:
			print("Cannot contiune because entry.tp is invalid. Please check the error message above. and try again.")
			return 0
	else:
		print(f"Warning could not find {buildfile.PLUGIN_ENTRY}. Canceling build process.")
		return 0
	
	if not os.path.exists(buildfile.PLUGIN_ICON):
		print(f"Warning {buildfile.PLUGIN_ICON} does not exist. TouchPortal will use default plugin icon.")
	else:
		print(f"Found {buildfile.PLUGIN_ICON} adding it to packing list.")
		TPP_PACK_LIST[buildfile.PLUGIN_ICON.split("/")[-1]] = buildfile.PLUGIN_ROOT + "/" \
			 if len(buildfile.PLUGIN_ICON.split("/")) == 1 else "".join(buildfile.PLUGIN_ICON.split("/")[0:-1])

	print(f"Compiling {buildfile.PLUGIN_MAIN} for {sys.platform}")

	PI_RUN = [buildfile.PLUGIN_MAIN]
	PI_RUN.append(f'--distpath={distdir}')
	PI_RUN.append(f'--onefile')
	PI_RUN.append("--clean")
	if (buildfile.PLUGIN_EXE_NAME == ""):
		PI_RUN.append(f'--name={os.path.splitext(os.path.basename(buildfile.PLUGIN_MAIN))[0]}')
	else:
		PI_RUN.append(f'--name={buildfile.PLUGIN_EXE_NAME}')
	if buildfile.PLUGIN_EXE_ICON and os.path.isfile(buildfile.PLUGIN_EXE_ICON):
		PI_RUN.append(f"--icon={Path(buildfile.PLUGIN_EXE_ICON).resolve()}")

	PI_RUN.append(f"--specpath={distdir}")
	PI_RUN.append(f"--workpath={distdir}/build")

	PI_RUN.extend(buildfile.ADDITIONAL_PYINSTALLER_ARGS)

	print("Running pyinstaller with arguments:", " ".join(PI_RUN))
	PyInstaller.__main__.run(PI_RUN)
	print(f"Done compiling. adding to packing list:", buildfile.PLUGIN_EXE_NAME + EXE_SFX)
	TPP_PACK_LIST[filePath(distdir, buildfile.PLUGIN_EXE_NAME + EXE_SFX)] = buildfile.PLUGIN_ROOT + "/"
	print("Checking for any additional required files")
	for file in buildfile.ADDITIONAL_FILES:
		print(f"Adding {file} to plugin")
		TPP_PACK_LIST[os.path.basename(file)] = os.path.join(buildfile.PLUGIN_ROOT, os.path.split(file)[0])

	print("Packing everything into tpp file")
	build_distro(opsys, buildfile.PLUGIN_VERSION, buildfile.PLUGIN_EXE_NAME, TPP_PACK_LIST, buildfile.OUTPUT_PATH)

	build_clean(distdir)
	print("Done!")

	return 0

if __name__ == "__main__":
	sys.exit(main())

PLUGIN_MAIN = " "
"""
*REQUIRED*
PLUGIN_MAIN: This lets tppbuild know where your main python plugin file is located so it will know which file to compile.
Note: This can be ether relative or absolute to the main script.
"""

PLUGIN_EXE_NAME = " "
"""
*REQUIRED*
PLUGIN_EXE_NAME: This defines what you want your plugin executable to be named. tppbuild will also use this for the .tpp file in the format:
                `pluginname + "_v" + version + "_" + os_name + ".tpp"`
"""

PLUGIN_EXE_ICON = r" "
"""
*OPTIONAL*
PLUGIN_EXE_ICON: This should be a path to a .ico file. However if png is passed in, it will tries to automatically converted to ico. if `PILLOW` is installed.
"""

PLUGIN_ENTRY = " "
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

PLUGIN_ROOT = " "
""" 
*REQUIRED*
This is the root folder name that will be inside of .tpp
 """


PLUGIN_ICON = r" "
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
Any additional arguments to be passed to Pyinstaller.
"""

ADDITIONAL_TPPSDK_ARGS = []
"""
*OPTIONAL*
ADDITIONAL_TPPSDK_ARGS: This allows you to give additional arg when generating entry.tp
"""

import inspect

def validateBuild():
    """
    validateBuild() this takes no arguments. when It's called it will check for all
    required constants variable are vaild It will check if path is vaild, is a file etc... If 
    any error is found, It will list all the error during the process.
    """
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    constants = module.__dir__()
    os.chdir(os.path.split(module.__file__)[0])

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

def runBuild():
	"""
	runBuild() this takes no arguments. This is the same as `tppbuild file.py` you do not need to pass your build config,
	It will automatically find it.
	"""
	frame = inspect.stack()[1]
	module = inspect.getmodule(frame[0])
	file = module.__file__

	main([file])