"""Testing dashboard.py functions"""
# Third-party imports
from unittest.mock import MagicMock


# Local imports
from dashboard import get_payment_method_map


def add_1(a:int):
    return a + 1

print(add_1(1))


def test_get_payment_method_map():
    mock = MagicMock()
    mock[3] = 'fish'
    mock.__setitem__.assert_called_with(3, 'fish')
    mock.__getitem__.return_value = 'result'


