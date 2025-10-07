import pytest

from nifty_anilist.utils.model_utils import validate_fuzzy_date_int

def test_avatar_request():
    """The the fuzzy date integer validation."""
    # Negative number.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(-1)

    # Too few digits.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(12345)

    # Too many digits.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(123456789)

    # Invalid year.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(15000101)

    # Month is zero.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(20200001)

    # Month too big.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(20201301)

    # Day is zero.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(20200100)

    # Day too big.
    with pytest.raises(ValueError):
        validate_fuzzy_date_int(20200132)

    # Valid values.
    assert validate_fuzzy_date_int(20200101) == 20200101
    assert validate_fuzzy_date_int(19991231) == 19991231
    assert validate_fuzzy_date_int(19690714) == 19690714
