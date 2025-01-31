"""Testing dashboard.py functions"""
# Third-party imports
from unittest.mock import patch

# Local imports
from dashboard import get_payment_method_map, get_truck_name_map

# Test the function using patching
@patch('dashboard.query')
def test_get_payment_method_map(mock_query):
    mock_query.return_value = [
        {"payment_method_id": 1, "payment_method": "cash"},
        {"payment_method_id": 2, "payment_method": "card"}
        ]
       
    expected = {"1": "cash", "2": "card"}
    assert get_payment_method_map(None) == expected

    mock_query.return_value = []
    assert get_payment_method_map(None) == {}
    

@patch('dashboard.query')
def test_get_truck_name_map(mock_query):
    mock_query.return_value = [
        {"truck_id": 1, "truck_name": "a truck"},
        {"truck_id": 2, "truck_name": "another truck"}
    ]
    expected = {"1": "a truck", "2": "another truck"}
    assert get_truck_name_map(None) == expected
