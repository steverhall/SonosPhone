#!/usr/bin/env python3
"""Start the ReadKey runner (calls the top-level ReadKey/readkey.py)."""
from ReadKey import readkey


if __name__ == '__main__':
    readkey.__main__() if hasattr(readkey, '__main__') else None
