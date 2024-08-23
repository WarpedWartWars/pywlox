from chunk import *
from common import *
#from value import *

def disassembleChunk(chunk: Chunk, name: str):
    print(f"== {name} ==", file=stdout)

    offset = 0
    while offset < len(chunk.code):
        offset = disassembleInstruction(chunk, offset)

def disassembleInstruction(chunk: Chunk, offset: int):
    print("%04d"%offset, end=" ", file=stdout)
    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        print("   | ", end="", file=stdout)
    else:
        print("%4d "%(chunk.lines[offset]), end="", file=stdout)

    instruction = chunk.code[offset]
    match instruction:
        case OP.CONSTANT:
            return constantInstruction("OP_CONSTANT", chunk, offset)
        case OP.NIL:
            return simpleInstruction("OP_NIL", offset)
        case OP.TRUE:
            return simpleInstruction("OP_TRUE", offset)
        case OP.FALSE:
            return simpleInstruction("OP_FALSE", offset)
        case OP.POP:
            return simpleInstruction("OP_POP", offset)
        case OP.GET_LOCAL:
            return byteInstruction("OP_GET_LOCAL", chunk, offset)
        case OP.SET_LOCAL:
            return byteInstruction("OP_SET_LOCAL", chunk, offset)
        case OP.GET_GLOBAL:
            return constantInstruction("OP_GET_GLOBAL", chunk, offset)
        case OP.DEFINE_GLOBAL:
            return constantInstruction("OP_DEFINE_GLOBAL", chunk, offset)
        case OP.SET_GLOBAL:
            return constantInstruction("OP_SET_GLOBAL", chunk, offset)
        case OP.GET_UPVALUE:
            return byteInstruction("OP_GET_UPVALUE", chunk, offset)
        case OP.SET_UPVALUE:
            return byteInstruction("OP_SET_UPVALUE", chunk, offset)
        case OP.GET_PROPERTY:
            return constantInstruction("OP_GET_PROPERTY", chunk, offset)
        case OP.SET_PROPERTY:
            return constantInstruction("OP_SET_PROPERTY", chunk, offset)
        case OP.GET_SUPER:
            return constantInstruction("OP_GET_SUPER", chunk, offset)
        case OP.EQUAL:
            return simpleInstruction("OP_EQUAL", offset)
        case OP.GREATER:
            return simpleInstruction("OP_GREATER", offset)
        case OP.LESS:
            return simpleInstruction("OP_LESS", offset)
        case OP.ADD:
            return simpleInstruction("OP_ADD", offset)
        case OP.SUBTRACT:
            return simpleInstruction("OP_SUBTRACT", offset)
        case OP.MULTIPLY:
            return simpleInstruction("OP_MULTIPLY", offset)
        case OP.DIVIDE:
            return simpleInstruction("OP_DIVIDE", offset)
        case OP.NOT:
            return simpleInstruction("OP_NOT", offset)
        case OP.NEGATE:
            return simpleInstruction("OP_NEGATE", offset)
        case OP.PRINT:
            return simpleInstruction("OP_PRINT", offset)
        case OP.JUMP:
            return jumpInstruction("OP_JUMP", 1, chunk, offset)
        case OP.JUMP_IF_FALSE:
            return jumpInstruction("OP_JUMP_IF_FALSE", 1, chunk, offset)
        case OP.LOOP:
            return jumpInstruction("OP_LOOP", -1, chunk, offset)
        case OP.CALL:
            return byteInstruction("OP_CALL", chunk, offset)
        case OP.INVOKE:
            return invokeInstruction("OP_INVOKE", chunk, offset)
        case OP.SUPER_INVOKE:
            return invokeInstruction("OP_SUPER_INVOKE", chunk, offset)
        case OP.CLOSURE:
            offset += 1
            constant = chunk.code[offset]
            offset += 1
            print("%-16s %4d %s"%
                  ("OP_CLOSURE",constant,chunk.constants[constant]),
                  file=stdout)

            function = chunk.constants[constant].as_function()
            for j in range(function.upvalueCount):
                isLocal = chunk.code[offset]
                index = chunk.code[offset+1]
                print("%04d      |                     %s %d"%
                      (offset,"local" if isLocal else "upvalue",index),
                      file=stdout)
                offset += 2
            return offset
        case OP.CLOSE_UPVALUE:
            return simpleInstruction("OP_CLOSE_UPVALUE", offset)
        case OP.RETURN:
            return simpleInstruction("OP_RETURN", offset)
        case OP.CLASS:
            return constantInstruction("OP_CLASS", chunk, offset)
        case OP.INHERIT:
            return simpleInstruction("OP_INHERIT", offset)
        case OP.METHOD:
            return constantInstruction("OP_METHOD", chunk, offset)
        case _:
            print(f"Unknown opcode {instruction}", file=stdout)
            return offset + 1

def simpleInstruction(name: str, offset: int):
    print(f"{name}", file=stdout)
    return offset + 1

def constantInstruction(name: str, chunk: Chunk, offset: int):
    constant = chunk.code[offset + 1]
    print("%-16s %4d '%s'"%
          (name,constant,chunk.constants[constant]),
          file=stdout)
    return offset + 2

def byteInstruction(name: str, chunk: Chunk, offset: int):
    print("%-16s %4d"%(name,chunk.code[offset + 1]), file=stdout)
    return offset + 2

def jumpInstruction(name: str, sign: int, chunk: Chunk, offset: int):
    jump = uint16_t(chunk.code[offset + 1] << 8)
    jump |= chunk.code[offset + 2]
    print("%-16s %4d -> %d"%
          (name,offset,offset+3+sign*jump),
          file=stdout)
    return offset + 3

def invokeInstruction(name: str, chunk: Chunk, offset: int):
    constant = chunk.code[offset + 1]
    argCount = chunk.code[offset + 2]
    print("%-16s (%d args) %4d '%s'"%
          (name,argCount,constant,chunk.constants[constant]),
          file=stdout)
    return offset + 3
