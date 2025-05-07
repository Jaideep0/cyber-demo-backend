# app/utils/email.py
import email
from typing import Dict, Any

def parse_email_headers(raw: str) -> Dict[str, Any]:
    msg = email.message_from_string(raw)
    return dict(msg.items())
