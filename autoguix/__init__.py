"""
AutoGUI-X: Modern macOS GUI Automation for Python

A fast, reliable, and modern GUI automation library specifically designed for macOS.
Compatible with PyAutoGUI's API.
"""

from typing import List, Optional

from PIL import Image

from autoguix.core.automation_core import AutomationCore
from autoguix.core.types import LocateMode, MouseButton, Point, Region, Size

__version__ = "0.1.0"
__author__ = "AutoGUI-X Contributors"
__license__ = "BSD-3-Clause"

# PyAutoGUI-compatible globals
PAUSE = 0.0
FAILSAFE = True
FAILSAFE_POINT = Point(0, 0)

# Global core instance
_core = AutomationCore()


# -- lifecycle ----------------------------------------------------------------


def init() -> None:
    """Initialize AutoGUI-X. Must be called before any other function."""
    _core.init()


def cleanup() -> None:
    """Release resources."""
    _core.cleanup()


# -- screen -------------------------------------------------------------------


def size() -> Size:
    """Return the primary screen size as a (width, height) Size tuple."""
    return _core.get_screen_size()


def screenshot(imageFilename: Optional[str] = None, region: Optional[Region] = None) -> Image.Image:
    """Take a screenshot, optionally saving to *imageFilename*."""
    img = _core.take_screenshot(region)
    if imageFilename:
        img.save(imageFilename)
    return img


# -- mouse --------------------------------------------------------------------


def position() -> Point:
    """Return the current mouse position as a (x, y) Point tuple."""
    return _core.get_mouse_position()


def moveTo(x: int, y: int, duration: float = 0.0) -> None:
    """Move the mouse to (x, y)."""
    _core.move_mouse(x, y, duration)


def click(
    x: Optional[int] = None,
    y: Optional[int] = None,
    clicks: int = 1,
    interval: float = 0.0,
    button: str = "left",
) -> None:
    """Click the mouse at (x, y)."""
    _core.click(x, y, MouseButton(button), clicks, interval)


def doubleClick(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """Double-click at (x, y)."""
    _core.click(x, y, MouseButton.LEFT, clicks=2, interval=0.0)


def rightClick(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """Right-click at (x, y)."""
    _core.click(x, y, MouseButton.RIGHT, clicks=1, interval=0.0)


def middleClick(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """Middle-click at (x, y)."""
    _core.click(x, y, MouseButton.MIDDLE, clicks=1, interval=0.0)


def scroll(clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
    """Scroll the mouse wheel. Positive = up, negative = down."""
    _core.scroll(clicks, x, y)


# -- keyboard -----------------------------------------------------------------


def press(key: str) -> None:
    """Press and release a single key."""
    _core.press_key(key)


def keyDown(key: str) -> None:
    """Press a key down (without releasing)."""
    _core.key_down(key)


def keyUp(key: str) -> None:
    """Release a key."""
    _core.key_up(key)


def typewrite(text: str, interval: float = 0.0) -> None:
    """Type a string of text character by character."""
    _core.type_text(text, interval)


def write(text: str, interval: float = 0.0) -> None:
    """Alias for typewrite()."""
    typewrite(text, interval)


def hotkey(*keys: str) -> None:
    """Press a combination of keys (e.g. hotkey('command', 'c'))."""
    _core.hotkey(*keys)


# -- locate -------------------------------------------------------------------


def locateOnScreen(
    image: str,
    confidence: float = 0.9,
    region: Optional[Region] = None,
) -> Optional[Region]:
    """Locate *image* on screen. Returns a Region or None."""
    return _core.locate_on_screen(image, confidence, region)


def locateAllOnScreen(
    image: str,
    confidence: float = 0.9,
    region: Optional[Region] = None,
) -> List[Region]:
    """Locate all occurrences of *image* on screen."""
    return _core.locate_all_on_screen(image, confidence, region)


def locateCenterOnScreen(
    image: str,
    confidence: float = 0.9,
    region: Optional[Region] = None,
) -> Optional[Point]:
    """Locate *image* on screen and return its center Point."""
    loc = locateOnScreen(image, confidence, region)
    if loc is None:
        return None
    return Point(loc.left + loc.width // 2, loc.top + loc.height // 2)


__all__ = [
    # lifecycle
    "init",
    "cleanup",
    # screen
    "size",
    "screenshot",
    # mouse
    "position",
    "moveTo",
    "click",
    "doubleClick",
    "rightClick",
    "middleClick",
    "scroll",
    # keyboard
    "press",
    "keyDown",
    "keyUp",
    "typewrite",
    "write",
    "hotkey",
    # locate
    "locateOnScreen",
    "locateAllOnScreen",
    "locateCenterOnScreen",
    # types
    "Point",
    "Size",
    "Region",
    "MouseButton",
    "LocateMode",
    # globals
    "PAUSE",
    "FAILSAFE",
    "FAILSAFE_POINT",
]
