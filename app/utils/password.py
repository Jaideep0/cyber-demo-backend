# app/utils/password.py

from zxcvbn import zxcvbn
from typing import Dict, Any

def score_password(pwd: str) -> Dict[str, Any]:
    """Returns zxcvbn analysis:
      - score (0–4)
      - crack_time (display)
      - feedback (warnings & suggestions)"""
   
    result = zxcvbn(pwd)
    return {
        "score": result["score"],
        "crack_time": result["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
        "feedback": result["feedback"],
    }
