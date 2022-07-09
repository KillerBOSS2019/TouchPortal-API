# Usage

## Generating entry.tp

This SDK tool provides features for generating and validating Touch Portal Plugin Description files,
which are in JSON format and typically named "entry.tp" (as described in the [TP API docs](https://www.touch-portal.com/api/)).

**Generation** is done based on dictionary structures defined in plugin scripts. These structures closely follow
the format of the description file JSON, but are further expanded to make them also useful within the plugin
scripts themselves. This avoids almost all the need for duplication of things like unique IDs, default values,
settings names, and so on, since those details need to be available in both the definition JSON and in the
script which will be using those definitions to communicate with Touch Portal.

**Validation** is performed on the generated descriptions, and can also be run against pre-existing definition files
as a sort of "lint" utility. Currently the following things are checked:
- All required attributes are present.
- All attribute values are of the supported data type(s).
- No unknown attributes are present.
- Attributes are valid for the TP SDK version being used.
- Attribute values fall within allowed list of values (if relevant, eg. `Action.type`).
- All ID strings are unique within the plugin (eg. for States, Actions, etc).

To generate entry.tp run following command:

```
tppsdk plugin-example.py
```

## Packaging plugin

This SDK tools will make usable .tpp file by compile, packaging and clean up.

tppbuild automatically do these steps:
- Generate entry.tp if you passed in .py file otherwise it will validate the .tp file and raise an error if it's not valid.
- Compile your main script for your system (Windows, MacOS, Linux) depending on the platform you're running on.
- Packaging all the required file for your plugin.
- Finally create the tpp file with its in this format pluginname_version_os.tpp

Note that running this script requires `pyinstaller` to be installed. You can install it by running `pip install pyinstaller` in your terminal.

To package your plugin into .tpp file run following command:

```
tppbuild example_build.py
```

## Generating Documentation

This SDK also provides a README.md generator if you don't want to write your own. the `Documentation.md`
in this folder is 100% auto generated from `plugin_example.py`

To generate another document
```
tppdoc plugin_example.py
```

## Cross platform compile (Github ONLY)

I've build a github action script that can run `tppbuild build.py` for Linux, Mac and Windows. The
script is simple to setup. let me expain.

1. In your own repository create a folder called `.github` and another folder in `.github` called `workflows` (You cannot use a custom name for this).
2. Then create a .yml file this can be named anything. and copy the content of `build.yml` in `.github/workflows` in this directory
3. If your plugin needs to be ran on a different version of python you can change that in your `.yml` file. default is `python-version: "3.10"`
4. You will also need to include `requirements.txt` by running `pip freeze > requirements.txt`
5. Last step you will also need to change the path to your own. eg `examplePlugin/requirements.txt`, `examplePlugin/build.py` and `"./examplePlugin/*.tpp"` will not work for you.

Lastly Linux and MacOS requires a special file to launch it. you will need [@spdermn02](https://github.com/spdermn02) 's `start.sh` file. to use this file your `entry.tp` will need `plugin_start_cmd_mac` and `plugin_start_cmd_linux` with `sh %TP_PLUGIN_FOLDER%/your_plugin_folder/start.sh your_plugin_executable`





# Info
Feel free to use the example plugin as a starting point for your own plugin. if you have any questions feel free head over to [Discord #plugin-general](https://discord.gg/MgxQb8r) or create a [GitHub issue](https://github.com/KillerBOSS2019/TouchPortal-API/issues/new).
