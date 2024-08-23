from common import *
from value import *

class OP(enum):
    CONSTANT = enum_auto()
    NIL = enum_auto()
    TRUE = enum_auto()
    FALSE = enum_auto()
    POP = enum_auto()
    GET_LOCAL = enum_auto()
    SET_LOCAL = enum_auto()
    GET_GLOBAL = enum_auto()
    DEFINE_GLOBAL = enum_auto()
    SET_GLOBAL = enum_auto()
    GET_UPVALUE = enum_auto()
    SET_UPVALUE = enum_auto()
    GET_PROPERTY = enum_auto()
    SET_PROPERTY = enum_auto()
    GET_SUPER = enum_auto()
    EQUAL = enum_auto()
    GREATER = enum_auto()
    LESS = enum_auto()
    ADD = enum_auto()
    SUBTRACT = enum_auto()
    MULTIPLY = enum_auto()
    DIVIDE = enum_auto()
    NOT = enum_auto()
    NEGATE = enum_auto()
    PRINT = enum_auto()
    JUMP = enum_auto()
    JUMP_IF_FALSE = enum_auto()
    LOOP = enum_auto()
    CALL = enum_auto()
    INVOKE = enum_auto()
    SUPER_INVOKE = enum_auto()
    CLOSURE = enum_auto()
    CLOSE_UPVALUE = enum_auto()
    RETURN = enum_auto()
    CLASS = enum_auto()
    INHERIT = enum_auto()
    METHOD = enum_auto()

#class Chunk(bytearray):pass

class Chunk:
    def __init__(self):
        self.code: list[uint8_t] = bytearray() # yes bytearray isn't a list of our uint8_t,
        self.constants: list[Value] = []       # it's just an optimization (is it?)
        self.lines: list[int] = []

    def write(self, byte: uint8_t, line: int):
        #if byte > UINT8_MAX:
        self.code.append(byte)
        self.lines.append(line)

    def addConstant(self, value: Value):
        self.constants.append(value)
        return len(self.constants) - 1
