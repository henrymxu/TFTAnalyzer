"""Read-only programmatic interface to Teamfight Tactics.

This package deliberately exposes no way to send input to the game client.
It only reads data: the official Riot Games API for account/rank/match
history, and (optionally) a local screen reader for live in-match state.
"""

from tft.interface import TFTInterface

__version__ = "0.1.0"
__all__ = ["TFTInterface"]
