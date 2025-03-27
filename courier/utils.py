import random
import string

def generate_unique_tracking_number():
    """Generate a random 6-character tracking number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
