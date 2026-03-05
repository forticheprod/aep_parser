"""Render queue item enumerations for After Effects.

These enums match the values used in After Effects ExtendScript.
"""

from __future__ import annotations

from enum import IntEnum


class GetSettingsFormat(IntEnum):
    """Format for getting render settings.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/#outputmodulegetsettings
    """

    SPEC = 3412
    NUMBER = 3413
    NUMBER_SETTABLE = 3414
    STRING = 3415
    STRING_SETTABLE = 3416


class LogType(IntEnum):
    """Logging level for rendering.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/#renderqueueitemlogtype
    """

    ERRORS_ONLY = 3212
    ERRORS_AND_SETTINGS = 3213
    ERRORS_AND_PER_FRAME_INFO = 3214

    @classmethod
    def from_binary(cls, value: int) -> LogType:
        """Convert binary value to LogType."""
        try:
            return cls(value + 3212)
        except ValueError:
            return cls.ERRORS_ONLY


class RQItemStatus(IntEnum):
    """Status of a render queue item.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/#renderqueueitemstatus
    """

    WILL_CONTINUE = 3012
    NEEDS_OUTPUT = 3013
    UNQUEUED = 3014
    QUEUED = 3015
    RENDERING = 3016
    USER_STOPPED = 3017
    ERR_STOPPED = 3018
    DONE = 3019

    @classmethod
    def from_binary(cls, value: int) -> RQItemStatus:
        """Convert binary value to RQItemStatus."""
        try:
            return cls(value + 3013)
        except ValueError:
            return cls.UNQUEUED
