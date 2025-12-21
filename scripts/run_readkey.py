#!/usr/bin/env python3
"""Start the ReadKey runner (calls services/ReadKey/readkey.py)."""
from services.ReadKey import readkey


if __name__ == '__main__':
    readkey.__main__() if hasattr(readkey, '__main__') else None
