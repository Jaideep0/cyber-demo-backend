# app/utils/exif.py

import exifread
from io import BytesIO
from typing import Dict, Any

def extract_exif_from_bytes(data: bytes) -> Dict[str, Any]:
    """
    Read EXIF tags from the given image bytes and return a
    dict mapping tag names to their string values.
    """
    with BytesIO(data) as buf:
        tags = exifread.process_file(buf, details=False)
    return {tag: str(value) for tag, value in tags.items()}
