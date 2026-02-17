"""Abstract base class for platform backends."""

from abc import ABC, abstractmethod
from typing import List, Optional

from PIL import Image

from pyautox.core.types import LocateMode, MouseButton, Point, Region, Size


class BackendBase(ABC):
    """Abstract base for all platform backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend and verify platform requirements."""

    @abstractmethod
    async def cleanup(self) -> None:
        """Release resources held by the backend."""

    @abstractmethod
    async def get_mouse_position(self) -> Point:
        """Return the current mouse cursor position."""

    @abstractmethod
    async def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None:
        """Move the mouse cursor to (x, y)."""

    @abstractmethod
    async def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.0,
    ) -> None:
        """Perform a mouse click."""

    @abstractmethod
    async def scroll(
        self, clicks: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> None:
        """Scroll the mouse wheel."""

    @abstractmethod
    async def press_key(self, key: str) -> None:
        """Press and release a key."""

    @abstractmethod
    async def key_down(self, key: str) -> None:
        """Press a key down."""

    @abstractmethod
    async def key_up(self, key: str) -> None:
        """Release a key."""

    @abstractmethod
    async def type_text(self, text: str, interval: float = 0.0) -> None:
        """Type a string of text."""

    @abstractmethod
    async def hotkey(self, *keys: str) -> None:
        """Press a combination of keys simultaneously."""

    @abstractmethod
    async def get_screen_size(self) -> Size:
        """Return the primary screen dimensions."""

    @abstractmethod
    async def take_screenshot(self, region: Optional[Region] = None) -> Image.Image:
        """Capture a screenshot, optionally limited to *region*."""

    @abstractmethod
    async def locate_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> Optional[Region]:
        """Locate *image* on screen. Return the bounding Region or None."""

    @abstractmethod
    async def locate_all_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> List[Region]:
        """Locate all occurrences of *image* on screen."""
