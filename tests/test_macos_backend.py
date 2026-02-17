"""Tests for MacOSBackend.

These tests mock the Quartz CoreGraphics module so they can run
on any platform without requiring PyObjC.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pyautox.core.types import MouseButton, Point, Size


def _make_mock_cg():
    """Create a mock CoreGraphics module."""
    cg = MagicMock()

    # Screen
    cg.CGMainDisplayID.return_value = 0
    bounds = SimpleNamespace(size=SimpleNamespace(width=1920.0, height=1080.0))
    cg.CGDisplayBounds.return_value = bounds

    # Mouse position
    mock_event = MagicMock()
    cg.CGEventCreate.return_value = mock_event
    loc = SimpleNamespace(x=100.0, y=200.0)
    cg.CGEventGetLocation.return_value = loc

    # Mouse events
    cg.CGEventCreateMouseEvent.return_value = MagicMock()
    cg.CGEventSetIntegerValueField = MagicMock()
    cg.kCGEventMouseMoved = 5
    cg.kCGHIDEventTap = 0

    # Keyboard events
    cg.CGEventCreateKeyboardEvent.return_value = MagicMock()
    cg.CGEventGetFlags.return_value = 0
    cg.CGEventSetFlags = MagicMock()
    cg.CGEventKeyboardSetUnicodeString = MagicMock()

    # Scroll
    cg.CGEventCreateScrollWheelEvent.return_value = MagicMock()

    return cg


@pytest.fixture
def backend():
    """Create a MacOSBackend with a mocked CoreGraphics."""
    from pyautox.backends.macos_backend import MacOSBackend

    b = MacOSBackend()
    b._cg = _make_mock_cg()
    b._initialized = True
    return b


@pytest.mark.asyncio
class TestScreenOps:
    async def test_get_screen_size(self, backend):
        result = await backend.get_screen_size()
        assert result == Size(1920, 1080)

    async def test_get_mouse_position(self, backend):
        result = await backend.get_mouse_position()
        assert result == Point(100, 200)


@pytest.mark.asyncio
class TestMouseOps:
    async def test_move_mouse_instant(self, backend):
        await backend.move_mouse(300, 400)
        backend._cg.CGEventCreateMouseEvent.assert_called()
        backend._cg.CGEventPost.assert_called()

    async def test_click_at_position(self, backend):
        await backend.click(50, 60, MouseButton.LEFT, clicks=1)
        # Should create down + up events
        assert backend._cg.CGEventPost.call_count >= 2

    async def test_double_click(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.click(50, 60, MouseButton.LEFT, clicks=2)
        # 2 clicks = 4 posts (move is also a post, plus down+up×2)
        assert backend._cg.CGEventPost.call_count >= 4

    async def test_right_click(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.click(50, 60, MouseButton.RIGHT, clicks=1)
        assert backend._cg.CGEventPost.call_count >= 2

    async def test_scroll(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.scroll(3)
        backend._cg.CGEventCreateScrollWheelEvent.assert_called_once()


@pytest.mark.asyncio
class TestKeyboardOps:
    async def test_key_down(self, backend):
        await backend.key_down("a")
        backend._cg.CGEventCreateKeyboardEvent.assert_called()

    async def test_key_up(self, backend):
        await backend.key_up("a")
        backend._cg.CGEventCreateKeyboardEvent.assert_called()

    async def test_press_key(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.press_key("a")
        assert backend._cg.CGEventPost.call_count == 2  # down + up

    async def test_type_text(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.type_text("hi")
        # 2 chars × 2 events (down + up) = 4
        assert backend._cg.CGEventPost.call_count == 4

    async def test_hotkey(self, backend):
        backend._cg.CGEventPost.reset_mock()
        await backend.hotkey("command", "c")
        # 2 keys down + 2 keys up = 4
        assert backend._cg.CGEventPost.call_count == 4

    async def test_unknown_key_raises(self, backend):
        with pytest.raises(ValueError, match="Unknown key"):
            await backend.press_key("nonexistent_key")


class TestNotInitialized:
    def test_ensure_ready_raises(self):
        from pyautox.backends.macos_backend import MacOSBackend

        b = MacOSBackend()
        with pytest.raises(RuntimeError, match="not initialized"):
            b._ensure_ready()
