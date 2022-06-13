
# Touch-Portal-Plugin-Example

![Downloads](https://img.shields.io/github/downloads/KillerBOSS2019/TP-YTDM-Plugin/total)
![Forks](https://img.shields.io/github/forks/KillerBOSS2019/TP-YTDM-Plugin)
![Stars](https://img.shields.io/github/stars/KillerBOSS2019/TP-YTDM-Plugin)
![License](https://img.shields.io/github/license/KillerBOSS2019/TP-YTDM-Plugin)
- [Touch Portal Plugin Example](#Touch-Portal-Plugin-Example)
  - [Description](#description)
    - [Settings Overview](#Settings-Overview)
  - [Features](#Features)
    - [Actions](#actions)
    - [States](#states)
  - [Installation Guide](#installation)
  - [Bugs and Support](#Bugs-and-Suggestion)
  - [License](#license)
  

# Description
This is an example plugin for Touch Portal. It demonstrates the basics of how to create a plugin, and how to communicate with Touch Portal.
    
## Settings Overview
### example
| Read-only | Type | Default Value |
| --- | --- | --- |
| False | text | Example value |

Example setting doc


# Features

## Actions
<table>
<tr valign='buttom'><th>Action Name</th><th>Description</th><th>Format</th><th nowrap>Data<br/><div align=left><sub>choices/default (in bold)</th><th>On<br/>Hold</sub></div></th></tr>
<tr valign='top'><td>example</td><td>This action sets the example setting to a given value, and also sets the color of the example setting to a given value.</td><td>Set Example State Text to [text] and Color to [2]</td><td><ul start=0>
<li>[text] Type: text &nbsp; 
<b>Hello World!</b></li>
<li>[color] Type: color &nbsp; 
<b>#818181FF</b></li>
</ul></td>
<td align=center>No</td>
<tr valign='top'><td>Inc/DecrVol</td><td>This action increases or decreases the process volume of the selected process.</td><td>[2][1]Volume to[3]</td><td><ul start=0>
<li>[AppChoice] Type: choice &nbsp; 
&lt;empty&gt;</li>
<li>[OptionList] Type: choice &nbsp; 
<b>Increase</b> ['Increase', 'Decrease', 'Set']</li>
<li>[Volume] Type: number &nbsp; 
<b>10</b> (0-100)</li>
</ul></td>
<td align=center>No</td>
<tr valign='top'><td>AppMute</td><td>This action mutes or unmutes the selected process.</td><td>[2] Program:[1]</td><td><ul start=0>
<li>[appChoice] Type: choice &nbsp; 
&lt;empty&gt;</li>
<li>[OptionList] Type: choice &nbsp; 
<b>Toggle</b> ['Mute', 'Unmute', 'Toggle']</li>
</ul></td>
<td align=center>No</td>
</table>

### States
 <b>Base Id:</b> tp.plugin.example.python.

| Id | Name | Description | DefaultValue |
| --- | --- | --- | --- |
| .state.text | text | Example State Text | Hello World! |
| .state.color | color | Example State Color | #818181FF |



# Installation
1. Download .tpp file
2. in TouchPortal gui click gear icon and select 'Import Plugin'
3. Select the .tpp file
4. Click 'Import'
# Bugs and Suggestion
Open an [issue](https://github.com/KillerBOSS2019/TP-YTDM-Plugin/issues) or join offical [TouchPortal Discord](https://discord.gg/MgxQb8r) for support.


# License
This plugin is licensed under the [GPL 3.0 License] - see the [LICENSE](LICENSE) file for more information.

