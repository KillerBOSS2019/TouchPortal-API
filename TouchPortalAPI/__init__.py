"""
Python API and SDK for Touch Portal.

.. include:: ../README.md
"""
__copyright__ = """
    This file is part of the TouchPortal-API project.
    Copyright (C) 2021 DamienS

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

__version__ = "1.6"  # this is read from setup.py and possibly other places

# maintain backwards compatability
from . client import Client, TYPES
from . tools import Tools
