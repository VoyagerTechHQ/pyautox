"""Central orchestration layer that bridges user-facing API and platform backend."""

import asyncio
import sys
from typing import List, Optional

from PIL import Image

from autoguix.core.backend_base import BackendBase
from autoguix.core.types import LocateMode, MouseButton, Point, Region, Size


def _run(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an already-running event loop (e.g. Jupyter).
        # Create a new thread to avoid blocking.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


class AutomationCore:
    """High-level automation core that delegates to a platform backend."""

    def __init__(self) -> None:
        self._backend: Optional[BackendBase] = None
        self._initialized = False

    def _ensure_initialized(self) -> BackendBase:
        if not self._initialized or self._backend is None:
            raise RuntimeError(
                "AutoGUI-X is not initialized. Call autoguix.init() first."
            )
        return self._backend

    # -- lifecycle ------------------------------------------------------------

    def init(self) -> None:
        """Detect platform and initialize the appropriate backend."""
        if self._initialized:
            return
        if sys.platform != "darwin":
            raise OSError(
                f"AutoGUI-X currently only supports macOS, got platform={sys.platform!r}"
            )
        from autoguix.backends.macos_backend import MacOSBackend

        self._backend = MacOSBackend()
        _run(self._backend.initialize())
        self._initialized = True

    def cleanup(self) -> None:
        if self._backend is not None:
            _run(self._backend.cleanup())
        self._backend = None
        self._initialized = False

    # -- screen ---------------------------------------------------------------

    def get_screen_size(self) -> Size:
        return _run(self._ensure_initialized().get_screen_size())

    def take_screenshot(self, region: Optional[Region] = None) -> Image.Image:
        return _run(self._ensure_initialized().take_screenshot(region))

    # -- mouse ----------------------------------------------------------------

    def get_mouse_position(self) -> Point:
        return _run(self._ensure_initialized().get_mouse_position())

    def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None:
        _run(self._ensure_initialized().move_mouse(x, y, duration))

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.0,
    ) -> None:
        _run(self._ensure_initialized().click(x, y, button, clicks, interval))

    def scroll(
        self, clicks: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> None:
        _run(self._ensure_initialized().scroll(clicks, x, y))

    # -- keyboard -------------------------------------------------------------

    def press_key(self, key: str) -> None:
        _run(self._ensure_initialized().press_key(key))

    def key_down(self, key: str) -> None:
        _run(self._ensure_initialized().key_down(key))

    def key_up(self, key: str) -> None:
        _run(self._ensure_initialized().key_up(key))

    def type_text(self, text: str, interval: float = 0.0) -> None:
        _run(self._ensure_initialized().type_text(text, interval))

    def hotkey(self, *keys: str) -> None:
        _run(self._ensure_initialized().hotkey(*keys))

    # -- locate ---------------------------------------------------------------

    def locate_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> Optional[Region]:
        return _run(
            self._ensure_initialized().locate_on_screen(image, confidence, region, mode)
        )

    def locate_all_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> List[Region]:
        return _run(
            self._ensure_initialized().locate_all_on_screen(
                image, confidence, region, mode
            )
        )
