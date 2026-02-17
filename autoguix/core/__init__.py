"""Core module for AutoGUI-X."""

from autoguix.core.automation_core import AutomationCore
from autoguix.core.backend_base import BackendBase
from autoguix.core.types import LocateMode, MouseButton, Point, Region, Size

__all__ = [
    "AutomationCore",
    "BackendBase",
    "LocateMode",
    "MouseButton",
    "Point",
    "Region",
    "Size",
]
