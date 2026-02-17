"""Core data types for AutoGUI-X."""

from enum import Enum
from typing import NamedTuple


class Point(NamedTuple):
    """A point on the screen."""

    x: int
    y: int


class Size(NamedTuple):
    """Screen or window dimensions."""

    width: int
    height: int


class Region(NamedTuple):
    """A rectangular region on the screen."""

    left: int
    top: int
    width: int
    height: int


class MouseButton(Enum):
    """Mouse button identifiers."""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class LocateMode(Enum):
    """Image location strategy."""

    IMAGE = "image"
    OBJECT = "object"
