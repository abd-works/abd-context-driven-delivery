from unittest.mock import patch


@patch("./calculate_discount")
def test_apply(mock_calc):
    mock_calc.return_value = 0
