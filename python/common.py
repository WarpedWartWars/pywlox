from enum import IntEnum as _enum, auto as enum_auto
from sys import stdout, stderr
from io import StringIO
from stdint import *
class enum(_enum):
    """Enum where members are also (and must be) type uint8_t"""

DEBUG_PRINT_CODE = False
DEBUG_TRACE_EXECUTION = False
stdout=StringIO()
stderr=StringIO()

UINT8_COUNT = UINT8_MAX + 1
