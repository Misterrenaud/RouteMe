import pytest as pytest

from main import norm_lat, norm_lon, Coordinates, snail_generator

data_test_norm_lat = [
    (0, 0),
    (40, 40),
    (90, 90),
    (100, 80),
    (-100, -80),
    (360, 0),
]


@pytest.mark.parametrize("test_input,expected", data_test_norm_lat)
def test_norm_lat(test_input, expected):
    assert norm_lat(test_input) == expected


data_test_norm_lon = [
    (0, 0),
    (40, 40),
    (-190, 170),
    (200, -160),
    (-100, -100),
    (360, 0),
]


@pytest.mark.parametrize("test_input,expected", data_test_norm_lon)
def test_norm_lon(test_input, expected):
    assert norm_lon(test_input) == expected


def test_snail_generator():
    expected = [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (-1, 2),
        (0, 2),
    ]
    it = snail_generator(Coordinates(0, 0), 1)
    for i, exp in enumerate(expected):
        assert next(it) == Coordinates(*exp), f"Failed on element {i}: {exp}"
