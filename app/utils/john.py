# app/utils/john.py

import subprocess
import re
from typing import Optional


def get_john_speed() -> Optional[float]:
    """
    Run `john --test` to benchmark default format cracking speed.
    Returns guesses-per-second as a float, or None on failure.
    """
    try:
        proc = subprocess.run(
            ["john", "--test"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        return None

    # Parse any line containing "c/s"
    for line in proc.stdout.splitlines():
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)([KMG]?)\s*c/s", line)
        if m:
            value = float(m.group(1))
            unit = m.group(2)
            if unit == "K":
                value *= 1e3
            elif unit == "M":
                value *= 1e6
            elif unit == "G":
                value *= 1e9
            return value
    return None


def estimate_space(password: str) -> int:
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"[0-9]", password):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", password):
        pool += 32
    return pool ** len(password) if pool else 0


def format_seconds(sec: float) -> str:
    intervals = [
        ("year", 31536000),
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]
    parts = []
    for name, count in intervals:
        if sec >= count:
            val = int(sec // count)
            parts.append(f"{val} {name}{'s' if val != 1 else ''}")
            sec %= count
    return ", ".join(parts) or "under a second"


def generate_feedback(sec: float) -> str:
    if sec < 1:
        return "🚨 Instantly cracked! Needs work."
    if sec < 60:
        return "😬 Weak—will be cracked in seconds."
    if sec < 3600:
        return "🤔 Meh—about minutes to crack."
    if sec < 86400:
        return "👍 Not bad—it'll take hours."
    if sec < 31536000:
        return "💪 Strong—it'll take days."
    return "🛡️ Very strong—years to crack!"
