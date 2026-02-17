"""Tests for AutomationCore with a mock backend."""

from unittest.mock import patch

import pytest

from pyautox.core.automation_core import AutomationCore
from pyautox.core.backend_base import BackendBase
from pyautox.core.types import MouseButton, Point, Region, Size


class MockBackend(BackendBase):
    """A fully mocked backend for testing the core layer."""

    def __init__(self):
        self.initialized = False

    async def initialize(self):
        self.initialized = True

    async def cleanup(self):
        self.initialized = False

    async def get_mouse_position(self):
        return Point(100, 200)

    async def move_mouse(self, x, y, duration=0.0):
        pass

    async def click(self, x=None, y=None, button=MouseButton.LEFT, clicks=1, interval=0.0):
        pass

    async def scroll(self, clicks, x=None, y=None):
        pass

    async def press_key(self, key):
        pass

    async def key_down(self, key):
        pass

    async def key_up(self, key):
        pass

    async def type_text(self, text, interval=0.0):
        pass

    async def hotkey(self, *keys):
        pass

    async def get_screen_size(self):
        return Size(1920, 1080)

    async def take_screenshot(self, region=None):
        from PIL import Image
        return Image.new("RGB", (100, 100))

    async def locate_on_screen(self, image, confidence=0.9, region=None, mode=None):
        return Region(10, 20, 50, 50)

    async def locate_all_on_screen(self, image, confidence=0.9, region=None, mode=None):
        return [Region(10, 20, 50, 50)]


class TestAutomationCoreLifecycle:
    def test_not_initialized_raises(self):
        core = AutomationCore()
        with pytest.raises(RuntimeError, match="not initialized"):
            core.get_screen_size()

    def test_init_on_non_darwin_raises(self):
        core = AutomationCore()
        with patch("pyautox.core.automation_core.sys") as mock_sys:
            mock_sys.platform = "linux"
            with pytest.raises(OSError, match="only supports macOS"):
                core.init()

    def test_cleanup_resets_state(self):
        core = AutomationCore()
        core._backend = MockBackend()
        core._initialized = True
        core.cleanup()
        assert core._backend is None
        assert core._initialized is False


class TestAutomationCoreDelegation:
    """Verify that core methods delegate to the backend correctly."""

    def setup_method(self):
        self.core = AutomationCore()
        self.core._backend = MockBackend()
        self.core._initialized = True

    def test_get_screen_size(self):
        result = self.core.get_screen_size()
        assert result == Size(1920, 1080)

    def test_get_mouse_position(self):
        result = self.core.get_mouse_position()
        assert result == Point(100, 200)

    def test_move_mouse(self):
        self.core.move_mouse(50, 60)  # should not raise

    def test_click(self):
        self.core.click(10, 20, MouseButton.LEFT, 1, 0.0)

    def test_press_key(self):
        self.core.press_key("a")

    def test_type_text(self):
        self.core.type_text("hello")

    def test_hotkey(self):
        self.core.hotkey("command", "c")

    def test_scroll(self):
        self.core.scroll(3, 100, 200)

    def test_take_screenshot(self):
        img = self.core.take_screenshot()
        assert img is not None

    def test_locate_on_screen(self):
        result = self.core.locate_on_screen("test.png")
        assert result == Region(10, 20, 50, 50)

    def test_locate_all_on_screen(self):
        results = self.core.locate_all_on_screen("test.png")
        assert len(results) == 1
