from common import *
from object import *

class VAL(enum):
    BOOL = enum_auto()
    NIL = enum_auto()
    NUMBER = enum_auto()
    OBJ = enum_auto()

class Value:
    def __init__(self, type_: VAL, value: bool|float|Obj):
        self.type = type_
        self.as_ = value

    def __bool__(self):
        return bool(self.as_)

    def __float__(self):
        return float(self.as_)

    def __str__(self):
        match self.type:
            case VAL.BOOL: return "true" if bool(self) else "false"
            case VAL.NIL: return "nil"
            case VAL.NUMBER: return "%g"%float(self)
            case VAL.OBJ: return str(self.as_)

    def __eq__(self, other):
        if not isinstance(other, Value): return False
        if self.type != other.type: return False
        match self.type: #return self.as_ == other.as_
            case VAL.BOOL:   return bool(self) == bool(other)
            case VAL.NIL:    return True
            case VAL.NUMBER: return float(self) == float(other)
            case VAL.OBJ:    return self.as_obj() == other.as_obj()
            case _:          return False # Unreachable.

    def as_obj(self):
        if not self.is_obj(): return
        return self.as_ #reutnr lmao

    def obj_type(self):
        return self.as_.type#self.as_obj().type

    def is_class(self):
        return self.is_obj() and self.as_.type == OBJ.CLASS#self.isObjType(OBJ.CLASS)

    def is_bound_method(self):
        return self.is_obj() and self.as_.type == OBJ.BOUND_METHOD#self.isObjType(OBJ.BOUND_METHOD)

    def is_instance(self):
        return self.is_obj() and self.as_.type == OBJ.INSTANCE#self.isObjType(OBJ.INSTANCE)

    def is_closure(self):
        return self.is_obj() and self.as_.type == OBJ.CLOSURE#self.isObjType(OBJ.CLOSURE)

    def is_function(self):
        return self.is_obj() and self.as_.type == OBJ.FUNCTION#self.isObjType(OBJ.FUNCTION)

    def is_native(self):
        return self.is_obj() and self.as_.type == OBJ.NATIVE#self.isObjType(OBJ.NATIVE)

    def is_string(self):
        return self.is_obj() and self.as_.type == OBJ.STRING#self.isObjType(OBJ.STRING)

    def isObjType(self, type: OBJ):
        return self.is_obj() and self.as_.type == type

    def as_class(self):
        return self.as_#ObjClass(self.as_)

    def as_bound_method(self):
        return self.as_#ObjBoundMethod(self.as_)

    def as_instance(self):
        return self.as_#ObjInstance(self.as_)

    def as_closure(self):
        return self.as_#ObjClosure(self.as_)

    def as_function(self):
        return self.as_#ObjFunction(self.as_)

    def as_native(self):
        return self.as_.function#ObjNative(self.as_).function

    def as_string(self):
        return self.as_#ObjString(self.as_)

    def as_str(self):
        return self.as_.as_#str(self.as_)#str(self.as_string())

    def is_bool(self):
        return self.type == VAL.BOOL

    def is_nil(self):
        return self.type == VAL.NIL

    def is_number(self):
        return self.type == VAL.NUMBER

    def is_obj(self):
        return self.type == VAL.OBJ

    @staticmethod
    def from_bool(value: bool):
        return Value(VAL.BOOL, value)

    @staticmethod
    def nil():
        return Value(VAL.NIL, 0)

    @staticmethod
    def from_float(value: float):
        return Value(VAL.NUMBER, value)

    @staticmethod
    def from_obj(value: Obj):
        return Value(VAL.OBJ, value)

#class ValueArray(list):pass

#class ValueArray:
#    def __init__(self):
#        self.values: list[Value] = []
#
#    def __len__(self):
#        return len(self.values)
#
#    def write(self, value: Value):
#        self.values.append(value)
