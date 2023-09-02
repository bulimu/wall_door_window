# IFCModelGenerator

IFCModelGenerator is a Python script that generates IFC (Industry Foundation Classes) models for building information modeling (BIM) applications. It allows you to create walls, openings, doors, and windows and establish relationships between these elements within an IFC file.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

## Features

- Create walls with customizable dimensions.
- Generate openings, doors, and windows with specified properties.
- Establish relationships between elements using IfcRelAggregates.
- Export the generated model to an IFC file.

### Prerequisites

- Python 3.x
- `ifcopenshell` Python library

You can install `ifcopenshell` using pip:

```
pip install ifcopenshell
```


### Usage


You can run the script from the command line as follows:

```
python wall_door_window.py
```
This will generate an IFC file named wall_door_window.ifc in the current directory. You can open this file with any IFC-compatible software to view the generated model.

View:

![wall](https://github.com/bulimu/wall_door_window/blob/main/wall_window_door.png)

