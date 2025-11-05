from app.main import clean_and_validate


def test_clean_and_validate_strips_whitespace():
    payload = {
        "first_name": " Alice ",
        "last_name": " Smith\n",
        "phone_number": " (514) 555-1234 ",
        "address": " 123 Main St ",
    }

    cleaned = clean_and_validate(payload)

    assert cleaned["first_name"] == "Alice"
    assert cleaned["last_name"] == "Smith"
    assert cleaned["address"] == "123 Main St"
    assert cleaned["phone_number"] == "5145551234"


def test_clean_and_validate_rejects_short_phone():
    payload = {
        "first_name": "Bob",
        "last_name": "Jones",
        "phone_number": "12345",
        "address": "1 Test Ave",
    }

    cleaned = clean_and_validate(payload)

    assert cleaned["phone_number"] is None
