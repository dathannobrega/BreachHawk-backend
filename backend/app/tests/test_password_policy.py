import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.password_policy import validate_password


def test_validate_password_ok():
    assert validate_password('Abcdef1!') is None


def test_validate_password_fail_length():
    msg = validate_password('A1!')
    assert msg and 'caracteres' in msg

def test_validate_password_missing_uppercase():
    msg = validate_password('abcdef1!')
    assert msg and 'mai' in msg.lower()


def test_validate_password_missing_number():
    msg = validate_password('Abcdefg!')
    assert msg and 'número' in msg.lower()

def test_validate_password_missing_symbol():
    msg = validate_password('Abcdef12')
    assert msg and 'símbolo' in msg.lower()
