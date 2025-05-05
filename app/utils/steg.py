# app/utils/steg.py

from stegano import lsb
from io import BytesIO
from PIL import Image


def embed_message(image_bytes: bytes, message: str) -> bytes:
    """
    Embed `message` into the given image bytes via LSB steganography.
    Returns the modified PNG bytes.
    """
    with BytesIO(image_bytes) as inp:
        img = Image.open(inp)
        secret = lsb.hide(img, message)
        out = BytesIO()
        secret.save(out, format="PNG")
        return out.getvalue()


def extract_message(image_bytes: bytes) -> str:
    """
    Reveal the hidden message from the given image bytes.
    """
    buf = BytesIO(image_bytes)
    img = Image.open(buf)
    # Pass the PIL Image object to lsb.reveal
    return lsb.reveal(img)
