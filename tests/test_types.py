"""Tests for core data types."""

from pyautox.core.types import LocateMode, MouseButton, Point, Region, Size


class TestPoint:
    def test_creation(self):
        p = Point(100, 200)
        assert p.x == 100
        assert p.y == 200

    def test_tuple_unpacking(self):
        x, y = Point(10, 20)
        assert x == 10
        assert y == 20

    def test_equality(self):
        assert Point(1, 2) == Point(1, 2)
        assert Point(1, 2) != Point(3, 4)

    def test_is_tuple(self):
        p = Point(5, 6)
        assert isinstance(p, tuple)
        assert p[0] == 5
        assert p[1] == 6


class TestSize:
    def test_creation(self):
        s = Size(1920, 1080)
        assert s.width == 1920
        assert s.height == 1080

    def test_tuple_unpacking(self):
        w, h = Size(800, 600)
        assert w == 800
        assert h == 600


class TestRegion:
    def test_creation(self):
        r = Region(10, 20, 100, 200)
        assert r.left == 10
        assert r.top == 20
        assert r.width == 100
        assert r.height == 200

    def test_tuple_unpacking(self):
        left, top, w, h = Region(1, 2, 3, 4)
        assert (left, top, w, h) == (1, 2, 3, 4)


class TestMouseButton:
    def test_values(self):
        assert MouseButton.LEFT.value == "left"
        assert MouseButton.RIGHT.value == "right"
        assert MouseButton.MIDDLE.value == "middle"

    def test_from_string(self):
        assert MouseButton("left") is MouseButton.LEFT


class TestLocateMode:
    def test_values(self):
        assert LocateMode.IMAGE.value == "image"
        assert LocateMode.OBJECT.value == "object"
