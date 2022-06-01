__copyright__ = """
This file is part of the TouchPortal-API project.
Copyright TouchPortal-API Developers
Copyright (c) 2021 Maxim Paperno
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

import importlib
import os
import sys
from zipfile import (ZipFile, ZIP_DEFLATED)
import PyInstaller.__main__
from argparse import ArgumentParser
from glob import glob
from shutil import rmtree
import json

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from sdk_tools import generateDefinitionFromScript, _validateDefinition

def getInfoFromBuildScript(script:str):
	try:
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
		zf.write(os.path.join(root, "."))
		for file in files:
			src = os.path.join(root, file)
			if os.path.isfile(src):
				dst = os.path.join(base_path, os.path.relpath(root, relroot), file)
				zf.write(src, dst)
			elif recurse and os.path.isdir(src):
				zip_dir(zf, src, base_path)

def build_distro(opsys, version, pluginname, packingList, output):
	os_name = "Windows" if opsys == OS_WIN else "MacOS"
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

def build_clean(morefile=None):
	print("Cleaning up...")
	files = glob("./*.spec")
	files.extend(glob("./*.exe"))
	files.extend(["./build", "__pycache__"])
	if morefile != None:
		files.extend(morefile)
	for file in files:
		if os.path.exists(file):
			print("removing: " + file)
			if os.path.isfile(file):
				os.remove(file)
			elif os.path.isdir(file):
				rmtree(file)
	print("")

EXE_SFX = ".exe" if sys.platform == "win32" else ""

OS_WIN = 1
OS_MAC = 2

def main():
	if sys.platform == "win32":
		opsys = OS_WIN
	elif sys.platform == "darwin":
		opsys = OS_MAC
	else:
		return "Unsupported OS: " + sys.platform

	parser = ArgumentParser(description=
		"Script to automatically compile a Python plugin into a standalone exe, generate entry.tp, and package them into importable tpp file."
	)

	parser.add_argument(
		"--target", metavar='<target>', required=True, type=str,
		help='A build script that contains some infomations about the plugin. ' +
		'Using given infomation about the plugin, this script will automatically build entry.tp (if given file is .py) and it will build the distro ' +
		'based on which operating system you\'re using.'
	)

	opts = parser.parse_args()
	del parser
	print("tppbuild started with target: " + opts.target)
	buildfile = getInfoFromBuildScript(opts.target)


	attri_list = ["PLUGIN_ENTRY", "PLUGIN_MAIN", "PLUGIN_ROOT", "Pyinstaller_arg",
				  "PLUGIN_EXE_NAME", "PLUGIN_ICON", "PLUGIN_ICON", "FileRequired",
				  "OUTPUT_PATH", "PLUGIN_VERSION"]

	checklist = [attri in dir(buildfile) for attri in attri_list]
	if all(checklist) == False:
		print(f"{opts.target} is missing these variables: ", " ".join([attri for attri in attri_list if attri not in dir(buildfile)]))
		return -1

	isPyEntry = False
	TPP_PACK_LIST = {}

	print(f"Building {buildfile.PLUGIN_EXE_NAME} v{buildfile.PLUGIN_VERSION} target(s) on {sys.platform}\n")

	"""
	Step 1
		Checking if python entry or entry.tp exists or not. and only move on if it exists
	Step 2
		If file is entry.tp It will automatically validdate.
	"""
	if os.path.isfile(buildfile.PLUGIN_ENTRY):
		if buildfile.PLUGIN_ENTRY.endswith(".py"):
			print("Generating entry.tp from " , buildfile.PLUGIN_ENTRY)
			sys.path.append(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), buildfile.PLUGIN_ENTRY))))
			generatedJson = generateDefinitionFromScript(os.path.join(os.getcwd(), buildfile.PLUGIN_ENTRY))
			with open("entry.tp", "w", encoding="utf-8") as f:
				json.dump(generatedJson, f, indent=4)
			print("Successfully generated entry.tp")
			isPyEntry = True
		else:
			result = _validateDefinition(buildfile.PLUGIN_ENTRY)
			if not result:
				print(f"Cannot contiune because entry.tp is invalid. Please check the error message above. and try again.")
				return 0 # Exit build process because entry.tp is invalid

		# If everything goes well It will add to TPP packing list
		print("Adding entry.tp to packing list.")
		TPP_PACK_LIST["entry.tp" if buildfile.PLUGIN_ENTRY.endswith(".py") else buildfile.PLUGIN_ENTRY] = buildfile.PLUGIN_ROOT + "/"
	else:
		print(f"Warning could not find {buildfile.PLUGIN_ENTRY}. Canceling build process.")
		return 0

	if not os.path.exists(buildfile.PLUGIN_ICON):
		print(f"Warning {buildfile.PLUGIN_ICON} does not exist. TouchPortal will use default plugin icon.")
	else:
		print(f"Found {buildfile.PLUGIN_ICON} adding it to packing list.")
		TPP_PACK_LIST[buildfile.PLUGIN_ICON.split("/")[-1]] = buildfile.PLUGIN_ROOT + "/" if len(buildfile.PLUGIN_ICON.split("/")) == 1 else "".join(buildfile.PLUGIN_ICON.split("/")[0:-1])

	print(f"Compiling {buildfile.PLUGIN_MAIN} for {sys.platform}")

	PI_RUN = [buildfile.PLUGIN_MAIN]
	PI_RUN.append(f'--distpath={buildfile.OUTPUT_PATH}')
	PI_RUN.append(f'--onefile')
	if (buildfile.PLUGIN_EXE_NAME == ""):
		PI_RUN.append(f'--name={os.path.splitext(os.path.basename(buildfile.PLUGIN_MAIN))[0]}')
	else:
		PI_RUN.append(f'--name={buildfile.PLUGIN_EXE_NAME}')
	if buildfile.PLUGIN_EXE_ICON and os.path.isfile(buildfile.PLUGIN_EXE_ICON):
		PI_RUN.append(f"--icon={buildfile.PLUGIN_EXE_ICON}")
	PI_RUN.extend(buildfile.Pyinstaller_arg)

	print("Running pyinstaller with arguments:", " ".join(PI_RUN))
	PyInstaller.__main__.run(PI_RUN)
	print(f"Done compiling. adding to packing list:", buildfile.PLUGIN_EXE_NAME + EXE_SFX)
	TPP_PACK_LIST[buildfile.PLUGIN_EXE_NAME + EXE_SFX] = buildfile.PLUGIN_ROOT + "/"

	print("Checking for any additional required files")
	for file in buildfile.FileRequired:
		print(f"Adding {file} to plugin")
		TPP_PACK_LIST[file.split("/")[-1]] = file.split("/")[0:-1]

	print("Packing everything into tpp file")
	build_distro(opsys, buildfile.PLUGIN_VERSION, buildfile.PLUGIN_EXE_NAME, TPP_PACK_LIST, buildfile.OUTPUT_PATH)

	print("Clean up any mess that's made from this.")
	build_clean(["entry.tp"] if isPyEntry else None)
	print("Done!")

	return 0

if __name__ == "__main__":
	sys.exit(main())