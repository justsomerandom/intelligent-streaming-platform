"""Validation and conversion helpers shared by stream launchers and the API."""

import re


BITRATE_PATTERN = re.compile(r"^([1-9]\d{0,6})([kKmM])?$")


def bitrate_to_kbps(value: str) -> int:
    """Convert a user-facing bitrate such as ``1M`` into x264's kbps value."""
    match = BITRATE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("bitrate must be a positive integer optionally suffixed with k or M")

    amount = int(match.group(1))
    suffix = match.group(2)
    if suffix in ("m", "M"):
        return amount * 1000
    return amount
