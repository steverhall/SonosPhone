from sonosphone.keypad import Keypad


def test_keypad_init():
    kp = Keypad(column_count=4)
    assert kp.column_count == 4
    assert hasattr(kp, 'get_key')
