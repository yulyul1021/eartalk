import secrets
import string


def generate_random_string(length: str = 8) -> str:
    res = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                  for _ in range(length))
    return res