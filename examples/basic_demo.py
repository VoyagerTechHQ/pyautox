#!/usr/bin/env python3
"""Basic AutoGUI-X demo.

Run this script to verify that AutoGUI-X is installed correctly
and that it can interact with your macOS desktop.

Usage:
    python examples/basic_demo.py
"""

import autoguix as ag


def main():
    # Initialize the library
    ag.init()

    # Screen info
    screen = ag.size()
    print(f"Screen size: {screen.width} x {screen.height}")

    # Mouse position
    pos = ag.position()
    print(f"Mouse position: ({pos.x}, {pos.y})")

    # Take a screenshot
    img = ag.screenshot()
    print(f"Screenshot captured: {img.size[0]}x{img.size[1]} pixels")

    # Save a screenshot to file
    ag.screenshot("demo_screenshot.png")
    print("Screenshot saved to demo_screenshot.png")

    # Clean up
    ag.cleanup()
    print("Done!")


if __name__ == "__main__":
    main()
