"""Core module for PyAutoX."""

from pyautox.core.automation_core import AutomationCore
from pyautox.core.backend_base import BackendBase
from pyautox.core.types import LocateMode, MouseButton, Point, Region, Size

__all__ = [
    "AutomationCore",
    "BackendBase",
    "LocateMode",
    "MouseButton",
    "Point",
    "Region",
    "Size",
]
