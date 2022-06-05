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

 This SDK tools makes compile, packaging and distribution of your plugin easier.

 These are the steps the tppbuild will do for you:
 - Generate entry.tp if you passed in .py file otherwise it will validate the .tp file and raise an error if it's not valid.
 - Compile your main script for your system (Windows, MacOS) depending on the platform you're running on.
 - Create a .tpp file with all the files include compiled script, (generated or existing) entry.tp file.
 - Also the .tpp file will be renamed into this format pluginname_version_os.tpp

Note that running this script requires `pyinstaller` to be installed. You can install it by running `pip install pyinstaller` in your terminal.

To package your plugin into .tpp file run following command:

```
tppbuild --target example_build.py
```

# Info
Feel free to use the example plugin as a starting point for your own plugin. if you have any questions feel free head over to [Discord #plugin-general](https://discord.gg/MgxQb8r) or create a [GitHub issue](https://github.com/KillerBOSS2019/TouchPortal-API/issues/new).
