from typing import Optional

def validate_fuzzy_date_int(value: Optional[int]) -> Optional[int]:
    """Check if a given integer follows the `YYYYMMDD` format. These kinds of integers are used in Anilist filters for dates."""

    if value is None:
        return value

    if value < 0:
        raise ValueError("Provided fuzzy date integer was negative.")
    
    as_string = str(abs(value))

    if not len(as_string) == 8:
        raise ValueError("Provided fuzzy date integer was not 8 digits long.")

    if int(as_string[0:4]) < 1800:
        raise ValueError("Provided fuzzy date integer has an invalid year (too early).")

    if int(as_string[4:6]) == 0:
        raise ValueError("Provided fuzzy date integer has an invalid month (0).")
    
    if int(as_string[4:6]) > 12:
        raise ValueError("Provided fuzzy date integer has an invalid month (>12).")

    if int(as_string[6:8]) == 0:
        raise ValueError("Provided fuzzy date integer has an invalid date (0).")
    
    if int(as_string[6:8]) > 31:
        raise ValueError("Provided fuzzy date integer has an invalid date (>31).")

    return value
