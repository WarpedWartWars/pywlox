from operator import add, sub, mul, gt, lt
def div(a, b):
    if b == 0:
        if a == 0:
            return float("nan")
        return a * float("inf")
    return a/b
import time
from types import FunctionType

from chunk import *
from common import *
from compiler import *
from debug import *
from object import *
from value import *

FRAMES_MAX = 64
STACK_MAX = FRAMES_MAX + UINT8_COUNT

class CallFrame:
    def __init__(self, closure: ObjClosure, slots: int):
        self.closure = closure
        self.ip = 0
        self.slots = slots

class INTERPRET(enum):
    OK = enum_auto()
    COMPILE_ERROR = enum_auto()
    RUNTIME_ERROR = enum_auto()

def isFalsey(value: Value):
    return value.is_nil() or (value.is_bool() and not bool(value))

def clockNative(argCount: int, args: list[Value]):
    return Value.from_float(time.time())

class VM:
    def __init__(self, compiler: Compiler=None):
        self.frames = []
        self.openUpvalues = None

        self.stack: list[Value] = []
        self.globals = {}

        self.compiler = compiler
        if compiler is None:
            self.compiler = Compiler(TYPE.SCRIPT)

        self.initString = "init"

        self.defineNative("clock", clockNative)

    def runtimeError(self, message: str):
        print(message, file=stderr)

        for frame in reversed(self.frames):
            function = frame.closure.function
            instruction = frame.ip - 1
            print(f"[line {function.chunk.lines[instruction]}] in ",
                  file=stderr,end="")
            if function.name is None:
                print("script",file=stderr)
            else:
                print(f"{function.name}()",file=stderr)
        self.stack.clear()
        self.frames.clear()

    def resetFromBruh(self):
        self.stack.clear()
        self.frames.clear()

    def interpret(self, source: str):
        function = self.compiler.compile(source)
        if function is None: return INTERPRET.COMPILE_ERROR

        closure = ObjClosure(function)
        self.stack.append(Value.from_obj(closure))
        self.call(closure, 0)

        result = self.run()
        self.resetFromBruh()
        return result

    def READ_BYTE(self):
        self.frames[-1].ip+=1
        return self.frames[-1].closure.function.chunk.code[self.frames[-1].ip-1]
    def READ_SHORT(self):
        a = self.READ_BYTE()
        b = self.READ_BYTE()
        return (a<<8)|b
    def READ_CONSTANT(self):
        return self.frames[-1].closure.function.chunk.constants[self.READ_BYTE()]
    def READ_STRING(self):return self.READ_CONSTANT().as_str()
    def BINARY_OP(self, valueType, op):
        if not (self.stack[-1].is_number() and self.peek(1).is_number()):
            self.runtimeError("Operands must be numbers.")
            return INTERPRET.RUNTIME_ERROR
        b = float(self.stack.pop())
        a = float(self.stack.pop())
        self.stack.append(valueType(op(a, b)))

    def run(self):
        frame = self.frames[-1]

        while True:
            if DEBUG_TRACE_EXECUTION:
                print("          ", end="", file=stdout)
                for slot in self.stack:
                    print("[ %s ]"%slot, end="", file=stdout)
                print(file=stdout)
                disassembleInstruction(frame.closure.function.chunk, frame.ip)
            instruction = self.READ_BYTE()
            match instruction:
                case OP.CONSTANT:
                    constant = self.READ_CONSTANT()
                    self.stack.append(constant)
                case OP.NIL: self.stack.append(Value.nil())
                case OP.TRUE: self.stack.append(Value.from_bool(True))
                case OP.FALSE: self.stack.append(Value.from_bool(False))
                case OP.POP: self.stack.pop()
                case OP.GET_LOCAL: self.stack.append(self.stack[frame.slots+self.READ_BYTE()])
                case OP.SET_LOCAL: self.stack[frame.slots+self.READ_BYTE()] = self.stack[-1]
                case OP.GET_GLOBAL:
                    name = self.READ_STRING()
                    if name not in self.globals:
                        self.runtimeError(f"Undefined variable '{name}'.")
                        return INTERPRET.RUNTIME_ERROR
                    self.stack.append(self.globals[name])
                case OP.DEFINE_GLOBAL:
                    name = self.READ_STRING()
                    self.globals[name] = self.stack[-1]
                    self.stack.pop()
                case OP.SET_GLOBAL:
                    name = self.READ_STRING()
                    if name not in self.globals:
                        self.runtimeError(f"Undefined variable '{name}'.")
                        return INTERPRET.RUNTIME_ERROR
                    self.globals[name] = self.stack[-1]
                case OP.GET_UPVALUE:
                    #slot = READ_BYTE()
                    upvalue = frame.closure.upvalues[self.READ_BYTE()]
                    if upvalue.location is None:
                        self.stack.append(upvalue.closed)
                    else:
                        self.stack.append(self.stack[upvalue.location])
                case OP.SET_UPVALUE:
                    #slot = READ_BYTE()
                    upvalue = frame.closure.upvalues[self.READ_BYTE()]
                    if upvalue.location is None:
                        upvalue.closed = self.stack[-1]
                    else:
                        self.stack[upvalue.location] = self.stack[-1]
                case OP.GET_PROPERTY:
                    if not self.stack[-1].is_instance():
                        self.runtimeError("Only instances have properties.")
                        return INTERPRET.RUNTIME_ERROR

                    instance = self.stack[-1].as_instance()
                    name = self.READ_STRING()

                    if name in instance.fields:
                        self.stack.pop()
                        self.stack.append(instance.fields[name])
                        continue

                    if not self.bindMethod(instance.klass, name):
                        return INTERPRET.RUNTIME_ERROR
                case OP.SET_PROPERTY:
                    if not self.peek(1).is_instance():
                        self.runtimeError("Only instances have fields.")
                        return INTERPRET.RUNTIME_ERROR

                    instance = self.peek(1).as_instance()
                    instance.fields[self.READ_STRING()] = self.stack[-1]
                    value = self.stack.pop()
                    self.stack.pop()
                    self.stack.append(value)
                case OP.GET_SUPER:
                    name = self.READ_STRING()
                    superclass = self.stack.pop().as_class()

                    if not self.bindMethod(superclass, name):
                        return INTERPRET.RUNTIME_ERROR
                case OP.EQUAL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(Value.from_bool(a == b))
                case OP.GREATER:
                    if(a:=self.BINARY_OP(Value.from_bool,gt))is not None:return a
                case OP.LESS:
                    if(a:=self.BINARY_OP(Value.from_bool,lt))is not None:return a
                case OP.ADD:
                    if self.stack[-1].is_string() and self.peek(1).is_string():
                        b = self.stack.pop().as_str()
                        a = self.stack.pop().as_str()
                        self.stack.append(Value.from_obj(ObjString(a + b)))
                    elif self.stack[-1].is_number() and self.peek(1).is_number():
                        b = float(self.stack.pop())
                        a = float(self.stack.pop())
                        self.stack.append(Value.from_float(a + b))
                    else:
                        self.runtimeError(
                            "Operands must be two numbers or two strings.")
                        return INTERPRET.RUNTIME_ERROR
                case OP.SUBTRACT:
                    if(a:=self.BINARY_OP(Value.from_float,sub))is not None:return a
                case OP.MULTIPLY:
                    if(a:=self.BINARY_OP(Value.from_float,mul))is not None:return a
                case OP.DIVIDE:
                    if(a:=self.BINARY_OP(Value.from_float,div))is not None:return a
                case OP.NOT:
                    self.stack.append(Value.from_bool(isFalsey(self.stack.pop())))
                case OP.NEGATE:
                    if not self.stack[-1].is_number():
                        self.runtimeError("Operand must be a number.")
                        return INTERPRET.RUNTIME_ERROR
                    self.stack.append(Value.from_float(-float(self.stack.pop())))
                case OP.PRINT:
                    print(self.stack.pop(), file=stdout)
                case OP.JUMP:
                    offset = self.READ_SHORT()
                    frame.ip += offset
                case OP.JUMP_IF_FALSE:
                    offset = self.READ_SHORT()
                    if isFalsey(self.stack[-1]): frame.ip += offset
                case OP.LOOP:
                    offset = self.READ_SHORT()
                    frame.ip -= offset
                case OP.CALL:
                    argCount = self.READ_BYTE()
                    if not self.callValue(self.peek(argCount), argCount):
                        return INTERPRET.RUNTIME_ERROR
                    frame = self.frames[-1]
                case OP.INVOKE:
                    method = self.READ_STRING()
                    argCount = self.READ_BYTE()
                    if not self.invoke(method, argCount):
                        return INTERPRET.RUNTIME_ERROR
                    frame = self.frames[-1]
                case OP.SUPER_INVOKE:
                    method = self.READ_STRING()
                    argCount = self.READ_BYTE()
                    superclass = self.stack.pop().as_class()
                    if not self.invokeFromClass(superclass, method, argCount):
                        return INTERPRET.RUNTIME_ERROR
                    frame = self.frames[-1]
                case OP.CLOSURE:
                    function = self.READ_CONSTANT().as_function()
                    closure = ObjClosure(function)
                    self.stack.append(Value.from_obj(closure))
                    for i in range(len(closure.upvalues)):
                        isLocal = self.READ_BYTE()
                        index = self.READ_BYTE()
                        if isLocal:
                            closure.upvalues[i] = self.captureUpvalue(frame.slots + index)
                        else:
                            closure.upvalues[i] = frame.closure.upvalues[index]
                case OP.CLOSE_UPVALUE:
                    self.closeUpvalues(len(self.stack) - 1)
                    self.stack.pop()
                case OP.RETURN:
                    result = self.stack.pop()
                    self.closeUpvalues(frame.slots)
                    self.frames.pop()
                    if len(self.frames) == 0:
                        self.stack.pop()
                        return INTERPRET.OK

                    for i in range(len(self.stack)-frame.slots):
                        self.stack.pop()
                    self.stack.append(result)
                    frame = self.frames[-1]
                case OP.CLASS:
                    self.stack.append(Value.from_obj(ObjClass(self.READ_STRING())))
                case OP.INHERIT:
                    superclass = self.peek(1)
                    if not superclass.is_class():
                        self.runtimeError("Superclass must be a class.")
                        return INTERPRET.RUNTIME_ERROR

                    subclass = self.stack[-1].as_class()
                    subclass.methods.update(superclass.as_class().methods)
                    self.stack.pop() # Subclass.
                case OP.METHOD:
                    self.defineMethod(self.READ_STRING())

    def peek(self, distance: int):
        return self.stack[-1 - distance]

    def callValue(self, callee: Value, argCount: int):
        if callee.is_obj():
            match callee.obj_type():
                case OBJ.BOUND_METHOD:
                    bound = callee.as_bound_method()
                    self.stack[-argCount - 1] = bound.reciever
                    return self.call(bound.method, argCount)
                case OBJ.CLASS:
                    klass = callee.as_class()
                    self.stack[-argCount - 1] = Value.from_obj(ObjInstance(klass))
                    if self.initString in klass.methods:
                        return self.call(klass.methods[self.initString].as_closure(), argCount)
                    elif argCount != 0:
                        self.runtimeError(f"Expected 0 arguments but got {argCount}.")
                        return False
                    return True
                case OBJ.CLOSURE:
                    return self.call(callee.as_closure(), argCount)
                case OBJ.NATIVE:
                    result = callee.as_native()(argCount, len(self.stack) - argCount)
                    for i in range(argCount + 1): self.stack.pop()
                    self.stack.append(result)
                    return True
                case _: # Non-callable object type.
                    pass
        self.runtimeError("Can only call functions and classes.")
        return False

    def call(self, closure: ObjClosure, argCount: int):
        if argCount != closure.function.arity:
            self.runtimeError(f"Expected {closure.function.arity} arguments but got {argCount}.")
            return False

        if len(self.frames) == FRAMES_MAX:
            self.runtimeError("Stack overflow.")
            return False # reutnr lmao

        self.frames.append(CallFrame(closure, len(self.stack)-argCount-1))
        return True

    def defineNative(self, name: str, function: FunctionType):
        self.globals[name] = Value.from_obj(ObjNative(function))

    def captureUpvalue(self, local: int):
        prevUpvalue = None
        upvalue = self.openUpvalues
        while upvalue is not None and upvalue.location > local:
            prevUpvalue = upvalue
            upvalue = upvalue.next

        if upvalue is not None and upvalue.location == local:
            return upvalue

        createdUpvalue = ObjUpvalue(local)
        createdUpvalue.next = upvalue

        if prevUpvalue is None:
            self.openUpvalues = createdUpvalue
        else:
            prevUpvalue.next = createdUpvalue

        return createdUpvalue

    def closeUpvalues(self, last: int):
        while (self.openUpvalues is not None and
               self.openUpvalues.location >= last):
            upvalue = self.openUpvalues
            upvalue.closed = self.stack[upvalue.location]
            upvalue.location = None
            self.openUpvalues = upvalue.next

    def defineMethod(self, name: ObjString):
        method = self.stack[-1]
        klass = self.peek(1).as_class()
        klass.methods[name] = method
        self.stack.pop()

    def bindMethod(self, klass: ObjClass, name: ObjString):
        if name not in klass.methods:
            self.runtimeError(f"Undefined property '{name}'.")
            return False

        bound = ObjBoundMethod(self.stack[-1], ObjClosure(klass.methods[name].as_closure()))
        self.stack.pop()
        self.stack.append(Value.from_obj(bound))
        return True

    def invoke(self, name: ObjString, argCount: int):
        reciever = self.stack[-argCount-1]

        if not reciever.is_instance():
            self.runtimeError("Only instances have methods.")
            return False

        instance = reciever.as_instance()

        if name in instance.fields:
            value = instance.fields[name]
            self.stack[-argCount-1] = value
            return self.callValue(value, argCount)

        return self.invokeFromClass(instance.klass, name, argCount)

    def invokeFromClass(self, klass: ObjClass, name: ObjString, argCount: int):
        if name not in klass.methods:
            self.runtimeError(f"Undefined property '{name}'.")
            return False
        return self.call(klass.methods[name].as_closure(), argCount)
