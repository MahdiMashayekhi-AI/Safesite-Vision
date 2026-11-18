"""SafeSite Vision - real-time PPE detection and safety-compliance analytics.

The end-to-end pipeline is:

    YOLO (Ultralytics) -> ByteTrack -> PPE-to-person association
        -> compliance rule engine -> temporal smoothing -> violation events

See ``docs/architecture.md`` for the design notes.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
