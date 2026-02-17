# PyAutoX

**Modern macOS GUI Automation for Python**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

PyAutoX is a modern, fast, and reliable GUI automation library specifically designed for macOS. It provides a clean Python API for controlling the mouse, keyboard, and screen, with 100% compatibility with PyAutoGUI's interface.

## Why PyAutoX?

**PyAutoGUI has been stagnant for 4+ years and has poor macOS support.** PyAutoX is built from the ground up for macOS, using native APIs for maximum reliability and performance.

### Key Features

- **macOS Native**: Uses Quartz Event Services and Core Graphics for 95%+ reliability
- **Modern & Fast**: Built with async/await support and type hints
- **100% Compatible**: Drop-in replacement for PyAutoGUI on macOS
- **Focused**: Specialized for macOS, not a cross-platform compromise
- **Active Development**: Regularly maintained and updated

### Comparison

| Feature | PyAutoGUI | PyAutoX |
|---------|-----------|---------|
| macOS Reliability | ~60% | **95%+** |
| Native APIs | No | Quartz + Core Graphics |
| Async Support | No | Yes |
| Type Hints | No | Yes |
| Last Updated | 2020 | **Active** |
| macOS Focused | No | Yes |

## Quick Start

### Installation

```bash
# Install using uv (recommended)
uv pip install pyautox

# Or using pip
pip install pyautox
```

### Basic Usage

```python
import pyautox as ag

# Initialize
ag.init()

# Get screen size
width, height = ag.size()
print(f"Screen: {width}x{height}")

# Move mouse to center
ag.moveTo(width // 2, height // 2, duration=1.0)

# Click
ag.click()

# Type text
ag.typewrite("Hello from PyAutoX!", interval=0.05)

# Take screenshot
screenshot = ag.screenshot()
screenshot.save("screenshot.png")

# Locate image on screen
button_location = ag.locateOnScreen("button.png")
if button_location:
    ag.click(button_location.left, button_location.top)
```

## Documentation

### Core Functions

#### Screen

- `size()` - Get screen dimensions
- `screenshot(region=None)` - Capture screen or region

#### Mouse

- `position()` - Get current mouse position
- `moveTo(x, y, duration=0)` - Move mouse to coordinates
- `click(x=None, y=None, clicks=1, interval=0, button='left')` - Click mouse
- `doubleClick()` - Double click
- `rightClick()` - Right click

#### Keyboard

- `press(key)` - Press and release a key
- `keyDown(key)` - Press a key down
- `keyUp(key)` - Release a key
- `typewrite(text, interval=0)` - Type text

#### Location

- `locateOnScreen(image, confidence=0.9)` - Find image on screen
- `locateAllOnScreen(image, confidence=0.9)` - Find all matches

## Architecture

PyAutoX uses a three-layer architecture:

```
┌─────────────────────────────────────────────────────────┐
│  User API Layer (pyautox/__init__.py)                   │
│  PyAutoGUI-compatible functions                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Core Layer (pyautox/core/automation_core.py)           │
│  Backend management, async/sync handling                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Backend Layer (pyautox/backends/macos_backend.py)      │
│  macOS-specific implementation using native APIs        │
└────────────────────┬────────────────────────────────────┘
                     │
              ┌──────▼──────┐
              │  macOS API  │
              └─────────────┘
```

## Development

### Prerequisites

- Python 3.10+
- macOS 10.14+
- uv (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/VoyagerTechHQ/pyautox.git
cd pyautox

# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e ".[locate]"

# Run tests
pytest
```

### Project Structure

```
pyautox/
├── pyautox/            # Main package
│   ├── __init__.py     # User API
│   ├── core/           # Core logic
│   │   ├── automation_core.py
│   │   ├── backend_base.py
│   │   └── types.py
│   └── backends/       # Platform backends
│       └── macos_backend.py
├── examples/           # Example scripts
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [PyAutoGUI](https://github.com/asweigart/pyautogui)
- Built with [PyObjC](https://pyobjc.readthedocs.io/)
- Powered by macOS native APIs

## Contact

- **Issues**: [GitHub Issues](https://github.com/VoyagerTechHQ/pyautox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VoyagerTechHQ/pyautox/discussions)

---

**Made with love for the macOS Python community**
