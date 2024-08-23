from types import FunctionType

import chunk
from common import *
import value as v

class OBJ(enum):
    BOUND_METHOD = enum_auto()
    CLASS = enum_auto()
    INSTANCE = enum_auto()
    CLOSURE = enum_auto()
    FUNCTION = enum_auto()
    NATIVE = enum_auto()
    STRING = enum_auto()
    UPVALUE = enum_auto()

class Obj:
    def __init__(self, value=None):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            return
        self.type = None
        self.as_ = value

    def __str__(self):
        return f"{self.as_}"

    def __eq__(self, other):
        if not isinstance(other, Obj): return False
        if self.type != other.type: return False
        return self.as_ == other.as_

class ObjClass(Obj):
    def __init__(self, value=None):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjClass):
                self.name = value.name
                self.methods = value.methods
                return
        else:
            self.type = OBJ.CLASS
            self.as_ = value
        self.name = value
        self.methods = {}

    def __str__(self):
        return f"{self.name}"

class ObjInstance(Obj):
    def __init__(self, value=None):
        if isinstance(value, Obj):          # TODO: move this check to __new__
            if isinstance(value, ObjClass): # would have to learn __new__ though
                self.type = OBJ.INSTANCE
                self.as_ = value
                self.klass = value
                self.fields = {}
                return
            self.type = value.type
            self.as_ = value.as_
            if isinstance(value, ObjInstance):
                self.klass = value.klass
                self.fields = value.fields
                return
        else:
            self.type = OBJ.INSTANCE
            self.as_ = value
        self.klass = value
        self.fields = {}

    def __str__(self):
        return f"{self.klass.name} instance"

class ObjBoundMethod(Obj):
    def __init__(self, value=None, method=None):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjBoundMethod):
                self.reciever = value.reciever
                self.method = value.method
                return
        else:
            self.type = OBJ.BOUND_METHOD
            self.as_ = method
        self.reciever = value
        self.method = method

    def __str__(self):
        return str(self.method)

    def __eq__(self, other):
        if not isinstance(other, Obj): return False
        if self.type != other.type: return False
        return self.as_ is other.as_

class ObjFunction(Obj):
    def __init__(self, value=None):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjFunction):
                self.arity = value.arity
                self.upvalueCount = value.upvalueCount
                self.chunk = value.chunk
                self.name = value.name
                return
        else:
            self.type = OBJ.FUNCTION
            self.as_ = value
        self.arity = 0
        self.upvalueCount = 0
        self.chunk = chunk.Chunk()
        self.name = None

    def __str__(self):
        if self.name is None:
            return "<script>"
        return f"<fn {self.name}>"

class ObjClosure(Obj):
    def __init__(self, value: ObjFunction):
        if isinstance(value, Obj):             # TODO: move this check to __new__
            if isinstance(value, ObjFunction): # would have to learn __new__ though
                self.type = OBJ.CLOSURE
                self.as_ = value
                self.function = value
                self.upvalues = []
                for i in range(value.upvalueCount):
                    self.upvalues.append(None)
                return
            self.type = value.type
            self.as_ = value.as_
            if isinstance(value, ObjClosure):
                self.function = value.function
                self.upvalues = value.upvalues
                return
        else:
            self.type = OBJ.CLOSURE
            self.as_ = value
        self.function = value
        self.upvalues = []

    def __str__(self):
        return str(self.function)

class ObjUpvalue(Obj):
    def __init__(self, value: int):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjUpvalue):
                self.location = value.location
                self.closed = value.closed
                self.next = value.next
                return
        else:
            self.type = OBJ.UPVALUE
            self.as_ = value
        self.location = value
        self.closed = v.Value.nil()
        self.next = None

    def __str__(self):
        return "upvalue"

class ObjNative(Obj):
    def __init__(self, value: FunctionType):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjNative):
                self.function = value.function
            else: self.function = None
        else:
            self.type = OBJ.NATIVE
            self.as_ = value
            if not hasattr(value, "__call__"):
                raise TypeError(f"'{type(value)}' object is not callable")
            self.function = value

    def __str__(self):
        return f"<native fn>"

class ObjString(Obj):
    def __init__(self, value: str):
        if isinstance(value, Obj): # TODO: move this check to __new__
            self.type = value.type # would have to learn __new__ though
            self.as_ = value.as_
            if isinstance(value, ObjString):
                self.hash_ = value.hash_
                return
        else:
            self.type = OBJ.STRING
            self.as_ = value
        self.hash_ = hash(self.as_)

    def __str__(self):
        return self.as_

    #def __hash__(self):
    #    hash = uint32_t(2166136261)
    #    for i in self.as_:
    #        hash ^= uint8_t(ord(i))
    #        hash *= 16777619
    #    return hash
