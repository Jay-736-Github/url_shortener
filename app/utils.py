# TODO: Implement utility functions here
# Consider functions for:
# - Generating short codes
# - Validating URLs
# - Any other helper functions you need


import random
import string
import validators

def generate_short_code():
    """Generates a random 6-character alphanumeric short code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

def is_valid_url(url):
    """Validates if the given string is a valid URL."""
    return validators.url(url) is True
