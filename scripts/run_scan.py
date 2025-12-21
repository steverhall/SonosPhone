#!/usr/bin/env python3
"""Start the ScanAlbum runner (calls ScanAlbum/scan.py)."""
from ScanAlbum import scan


if __name__ == '__main__':
    scan.__main__() if hasattr(scan, '__main__') else None
