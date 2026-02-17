"""macOS backend using Quartz / CoreGraphics via PyObjC."""

import asyncio
from typing import List, Optional

import numpy as np
from PIL import Image

from autoguix.core.backend_base import BackendBase
from autoguix.core.types import LocateMode, MouseButton, Point, Region, Size

# ---------------------------------------------------------------------------
# macOS keycode mapping  (Virtual Key Codes – Inside Macintosh)
# ---------------------------------------------------------------------------
_KEYCODE_MAP = {
    # letters
    "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04, "g": 0x05,
    "z": 0x06, "x": 0x07, "c": 0x08, "v": 0x09, "b": 0x0B, "q": 0x0C,
    "w": 0x0D, "e": 0x0E, "r": 0x0F, "y": 0x10, "t": 0x11, "u": 0x20,
    "i": 0x22, "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28, "n": 0x2D,
    "m": 0x2E, "o": 0x1F,
    # digits
    "1": 0x12, "2": 0x13, "3": 0x14, "4": 0x15, "5": 0x17, "6": 0x16,
    "7": 0x1A, "8": 0x1C, "9": 0x19, "0": 0x1D,
    # special keys
    "return": 0x24, "enter": 0x24, "tab": 0x30, "space": 0x31,
    "delete": 0x33, "backspace": 0x33, "escape": 0x35, "esc": 0x35,
    # modifiers
    "command": 0x37, "cmd": 0x37, "shift": 0x38, "capslock": 0x39,
    "option": 0x3A, "alt": 0x3A, "control": 0x3B, "ctrl": 0x3B,
    "rightshift": 0x3C, "rightoption": 0x3D, "rightcontrol": 0x3E,
    "fn": 0x3F,
    # function keys
    "f1": 0x7A, "f2": 0x78, "f3": 0x63, "f4": 0x76, "f5": 0x60,
    "f6": 0x61, "f7": 0x62, "f8": 0x64, "f9": 0x65, "f10": 0x6D,
    "f11": 0x67, "f12": 0x6F,
    # arrow keys
    "left": 0x7B, "right": 0x7C, "down": 0x7D, "up": 0x7E,
    # punctuation / symbols
    "-": 0x1B, "=": 0x18, "[": 0x21, "]": 0x1E, "\\": 0x2A,
    ";": 0x29, "'": 0x27, ",": 0x2B, ".": 0x2F, "/": 0x2C, "`": 0x32,
    # others
    "home": 0x73, "end": 0x77, "pageup": 0x74, "pagedown": 0x79,
    "forwarddelete": 0x75, "help": 0x72,
    "volumeup": 0x48, "volumedown": 0x49, "mute": 0x4A,
}

# Modifier key → CGEvent flag mapping
_MODIFIER_FLAGS = {
    "command": 1 << 20,  # kCGEventFlagMaskCommand
    "cmd": 1 << 20,
    "shift": 1 << 17,  # kCGEventFlagMaskShift
    "option": 1 << 19,  # kCGEventFlagMaskAlternate
    "alt": 1 << 19,
    "control": 1 << 18,  # kCGEventFlagMaskControl
    "ctrl": 1 << 18,
    "fn": 1 << 23,  # kCGEventFlagMaskSecondaryFn
}

# Button mapping: MouseButton → (down_event_type, up_event_type, cg_mouse_button)
_BUTTON_MAP = {
    MouseButton.LEFT: (1, 2, 0),   # kCGEventLeftMouseDown/Up
    MouseButton.RIGHT: (3, 4, 1),  # kCGEventRightMouseDown/Up
    MouseButton.MIDDLE: (25, 26, 2),  # kCGEventOtherMouseDown/Up
}


class MacOSBackend(BackendBase):
    """Backend implementation for macOS using Quartz CoreGraphics."""

    def __init__(self) -> None:
        self._cg = None
        self._initialized = False

    async def initialize(self) -> None:
        try:
            from Quartz import CoreGraphics

            self._cg = CoreGraphics
        except ImportError as exc:
            raise ImportError(
                "PyObjC is required on macOS. Install with: "
                "pip install pyobjc-framework-Quartz"
            ) from exc
        self._initialized = True

    async def cleanup(self) -> None:
        self._initialized = False
        self._cg = None

    def _ensure_ready(self):
        if not self._initialized or self._cg is None:
            raise RuntimeError("MacOSBackend not initialized")
        return self._cg

    # ── screen ───────────────────────────────────────────────────────────────

    async def get_screen_size(self) -> Size:
        cg = self._ensure_ready()
        main = cg.CGMainDisplayID()
        bounds = cg.CGDisplayBounds(main)
        return Size(int(bounds.size.width), int(bounds.size.height))

    async def take_screenshot(self, region: Optional[Region] = None) -> Image.Image:
        cg = self._ensure_ready()

        if region is not None:
            rect = cg.CGRectMake(region.left, region.top, region.width, region.height)
        else:
            rect = cg.CGRectInfinite

        image_ref = cg.CGWindowListCreateImage(
            rect,
            cg.kCGWindowListOptionOnScreenOnly,
            cg.kCGNullWindowID,
            cg.kCGWindowImageDefault,
        )
        if image_ref is None:
            raise RuntimeError("Failed to capture screenshot (CGWindowListCreateImage returned None)")

        width = cg.CGImageGetWidth(image_ref)
        height = cg.CGImageGetHeight(image_ref)
        bytes_per_row = cg.CGImageGetBytesPerRow(image_ref)

        data_provider = cg.CGImageGetDataProvider(image_ref)
        raw_data = cg.CGDataProviderCopyData(data_provider)

        # raw_data is BGRA on macOS
        arr = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, bytes_per_row // 4, 4))
        # trim to actual width (bytes_per_row may include padding)
        arr = arr[:, :width, :]
        # BGRA → RGB
        rgb = arr[:, :, [2, 1, 0]]
        return Image.fromarray(rgb, "RGB")

    # ── mouse ────────────────────────────────────────────────────────────────

    async def get_mouse_position(self) -> Point:
        cg = self._ensure_ready()
        event = cg.CGEventCreate(None)
        loc = cg.CGEventGetLocation(event)
        return Point(int(loc.x), int(loc.y))

    async def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None:
        cg = self._ensure_ready()
        if duration <= 0:
            event = cg.CGEventCreateMouseEvent(
                None, cg.kCGEventMouseMoved, (x, y), 0
            )
            cg.CGEventPost(cg.kCGHIDEventTap, event)
        else:
            start = await self.get_mouse_position()
            steps = max(int(duration * 100), 2)
            for i in range(1, steps + 1):
                t = i / steps
                cx = int(start.x + (x - start.x) * t)
                cy = int(start.y + (y - start.y) * t)
                event = cg.CGEventCreateMouseEvent(
                    None, cg.kCGEventMouseMoved, (cx, cy), 0
                )
                cg.CGEventPost(cg.kCGHIDEventTap, event)
                await asyncio.sleep(duration / steps)

    async def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.0,
    ) -> None:
        cg = self._ensure_ready()

        if x is not None and y is not None:
            await self.move_mouse(x, y)
        else:
            pos = await self.get_mouse_position()
            x, y = pos.x, pos.y

        down_type, up_type, cg_button = _BUTTON_MAP[button]

        for i in range(clicks):
            down_event = cg.CGEventCreateMouseEvent(
                None, down_type, (x, y), cg_button
            )
            cg.CGEventSetIntegerValueField(down_event, 1, i + 1)  # click count
            cg.CGEventPost(cg.kCGHIDEventTap, down_event)

            up_event = cg.CGEventCreateMouseEvent(
                None, up_type, (x, y), cg_button
            )
            cg.CGEventSetIntegerValueField(up_event, 1, i + 1)
            cg.CGEventPost(cg.kCGHIDEventTap, up_event)

            if interval > 0 and i < clicks - 1:
                await asyncio.sleep(interval)

    async def scroll(
        self, clicks: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> None:
        cg = self._ensure_ready()

        if x is not None and y is not None:
            await self.move_mouse(x, y)

        event = cg.CGEventCreateScrollWheelEvent(
            None,
            0,  # kCGScrollEventUnitLine
            1,  # one axis
            clicks,
        )
        cg.CGEventPost(cg.kCGHIDEventTap, event)

    # ── keyboard ─────────────────────────────────────────────────────────────

    def _resolve_keycode(self, key: str) -> int:
        code = _KEYCODE_MAP.get(key.lower())
        if code is None:
            raise ValueError(f"Unknown key: {key!r}")
        return code

    async def key_down(self, key: str) -> None:
        cg = self._ensure_ready()
        code = self._resolve_keycode(key)
        event = cg.CGEventCreateKeyboardEvent(None, code, True)
        # set modifier flag if it's a modifier key
        flag = _MODIFIER_FLAGS.get(key.lower())
        if flag:
            cg.CGEventSetFlags(event, cg.CGEventGetFlags(event) | flag)
        cg.CGEventPost(cg.kCGHIDEventTap, event)

    async def key_up(self, key: str) -> None:
        cg = self._ensure_ready()
        code = self._resolve_keycode(key)
        event = cg.CGEventCreateKeyboardEvent(None, code, False)
        cg.CGEventPost(cg.kCGHIDEventTap, event)

    async def press_key(self, key: str) -> None:
        await self.key_down(key)
        await self.key_up(key)

    async def type_text(self, text: str, interval: float = 0.0) -> None:
        cg = self._ensure_ready()
        for ch in text:
            # Use CGEventKeyboardSetUnicodeString for reliable Unicode input
            down = cg.CGEventCreateKeyboardEvent(None, 0, True)
            cg.CGEventKeyboardSetUnicodeString(down, len(ch), ch)
            cg.CGEventPost(cg.kCGHIDEventTap, down)

            up = cg.CGEventCreateKeyboardEvent(None, 0, False)
            cg.CGEventKeyboardSetUnicodeString(up, len(ch), ch)
            cg.CGEventPost(cg.kCGHIDEventTap, up)

            if interval > 0:
                await asyncio.sleep(interval)

    async def hotkey(self, *keys: str) -> None:
        cg = self._ensure_ready()
        # Press all keys down in order, then release in reverse
        flags = 0
        events_down = []
        for key in keys:
            code = self._resolve_keycode(key)
            mod_flag = _MODIFIER_FLAGS.get(key.lower())
            if mod_flag:
                flags |= mod_flag
            event = cg.CGEventCreateKeyboardEvent(None, code, True)
            cg.CGEventSetFlags(event, flags)
            events_down.append(event)

        for event in events_down:
            cg.CGEventPost(cg.kCGHIDEventTap, event)

        # Release in reverse order
        for key in reversed(keys):
            code = self._resolve_keycode(key)
            mod_flag = _MODIFIER_FLAGS.get(key.lower())
            if mod_flag:
                flags &= ~mod_flag
            event = cg.CGEventCreateKeyboardEvent(None, code, False)
            cg.CGEventSetFlags(event, flags)
            cg.CGEventPost(cg.kCGHIDEventTap, event)

    # ── locate ───────────────────────────────────────────────────────────────

    async def locate_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> Optional[Region]:
        try:
            import cv2
        except ImportError:
            raise ImportError(
                "OpenCV is required for image location. "
                "Install with: pip install 'autoguix[locate]'"
            )

        screenshot = await self.take_screenshot(region)
        screen_arr = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_arr, cv2.COLOR_RGB2GRAY)

        template = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Could not load template image: {image!r}")

        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < confidence:
            return None

        th, tw = template.shape[:2]
        ox = region.left if region else 0
        oy = region.top if region else 0
        return Region(max_loc[0] + ox, max_loc[1] + oy, tw, th)

    async def locate_all_on_screen(
        self,
        image: str,
        confidence: float = 0.9,
        region: Optional[Region] = None,
        mode: LocateMode = LocateMode.IMAGE,
    ) -> List[Region]:
        try:
            import cv2
        except ImportError:
            raise ImportError(
                "OpenCV is required for image location. "
                "Install with: pip install 'autoguix[locate]'"
            )

        screenshot = await self.take_screenshot(region)
        screen_arr = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_arr, cv2.COLOR_RGB2GRAY)

        template = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Could not load template image: {image!r}")

        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)

        th, tw = template.shape[:2]
        ox = region.left if region else 0
        oy = region.top if region else 0

        regions: List[Region] = []
        for pt in zip(*locations[::-1]):  # x, y
            regions.append(Region(int(pt[0]) + ox, int(pt[1]) + oy, tw, th))
        return regions
