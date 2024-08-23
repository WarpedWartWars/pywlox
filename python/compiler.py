from chunk import *
from common import *
from scanner import *
from object import *
from value import *

if DEBUG_PRINT_CODE:
    from debug import *

class PREC(enum):
    NONE = enum_auto()
    ASSIGNMENT = enum_auto()   # =
    OR = enum_auto()           # or
    AND = enum_auto()          # and
    EQUALITY = enum_auto()     # == !=
    COMPARISON = enum_auto()   # < > <= >=
    TERM = enum_auto()         # + -
    FACTOR = enum_auto()       # * /
    UNARY = enum_auto()        # ! -
    CALL = enum_auto()         # . ()
    PRIMARY = enum_auto()

from collections import namedtuple
ParseRule = namedtuple("ParseRule", ("prefix", "infix", "precedence"))
del namedtuple

class ClassCompiler:
    def __init__(self):
        self.enclosing = None
        self.hasSuperclass = None

class Local:
    def __init__(self, name: Token, depth: int, isCaptured: bool):
        self.name = name
        self.depth = depth
        self.isCaptured = isCaptured

class Upvalue:
    def __init__(self, index: uint8_t, isLocal: bool):
        self.index = index
        self.isLocal = isLocal

class TYPE(enum):
    FUNCTION = enum_auto()
    INITIALIZER = enum_auto()
    METHOD = enum_auto()
    SCRIPT = enum_auto()

class Parser:
    def __init__(self, scanner: Scanner=None):
        self.current = None
        self.previous = None
        self.hadError = None
        self.panicMode = None

        self.scanner = scanner
        if scanner is None:
            self.scanner = Scanner("")

    def advance(self):
        self.previous = self.current

        while True:
            self.current = self.scanner.scanToken()
            if self.current.type != TOKEN.ERROR: break

            self.errorAtCurrent(self.current.source)

    def consume(self, type: TOKEN, message: str):
        if self.current.type == type:
            self.advance()
            return

        self.errorAtCurrent(message)

    def match(self, type: TOKEN):
        if not self.check(type): return False
        self.advance()
        return True

    def check(self, type: TOKEN):
        return self.current.type == type

    def errorAtCurrent(self, message: str):
        self.errorAt(self.current, message)

    def error(self, message: str):
        self.errorAt(self.previous, message)

    def errorAt(self, token: Token, message: str):
        if self.panicMode: return
        self.panicMode = True
        print(f"[line {token.line}] Error", end="", file=stderr)

        if token.type == TOKEN.EOF:
            print(" at end", end="", file=stderr)
        elif token.type == TOKEN.ERROR:
            pass # Nothing.
        else:
            print(f" at '{token.source}'", end="", file=stderr)

        print(f": {message}", file=stderr)
        self.hadError = True

    def synchronize(self):
        self.panicMode = False

        while self.current.type != TOKEN.EOF:
            if self.previous.type == TOKEN.SEMICOLON: return
            match self.current.type:
                case TOKEN.CLASS: return
                case TOKEN.FUN: return
                case TOKEN.VAR: return
                case TOKEN.FOR: return
                case TOKEN.IF: return
                case TOKEN.WHILE: return
                case TOKEN.PRINT: return
                case TOKEN.RETURN: return

                case _: pass # Do nothing

            self.advance()

class Compiler:
    def __init__(self, type: TYPE, enclosing=None, parser: Parser=None, scanner: Scanner=None):
        self.locals = [Local(Token.synthetic(""), 0, False)]
        self.upvalues = []
        self.scopeDepth = 0
        self.enclosing = enclosing
        self.currentClass = None
        if enclosing is not None:
            self.currentClass = enclosing.currentClass
        self.function = ObjFunction()
        self.type = type
        if type != TYPE.FUNCTION:
            self.locals[0].name.source = "this"

        self.scanner = scanner
        self.parser = parser
        if scanner is None:
            self.scanner = Scanner("")
        if parser is None:
            self.parser = Parser(self.scanner)

        if type != TYPE.SCRIPT:
            self.function.name = ObjString(self.parser.previous.source)

        self.rules = {
            TOKEN.LEFT_PAREN    : ParseRule(self.grouping, self.call,   PREC.CALL),
            TOKEN.RIGHT_PAREN   : ParseRule(None,          None,        PREC.NONE),
            TOKEN.LEFT_BRACE    : ParseRule(None,          None,        PREC.NONE), 
            TOKEN.RIGHT_BRACE   : ParseRule(None,          None,        PREC.NONE),
            TOKEN.COMMA         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.DOT           : ParseRule(None,          self.dot,    PREC.CALL),
            TOKEN.MINUS         : ParseRule(self.unary,    self.binary, PREC.TERM),
            TOKEN.PLUS          : ParseRule(None,          self.binary, PREC.TERM),
            TOKEN.SEMICOLON     : ParseRule(None,          None,        PREC.NONE),
            TOKEN.SLASH         : ParseRule(None,          self.binary, PREC.FACTOR),
            TOKEN.STAR          : ParseRule(None,          self.binary, PREC.FACTOR),
            TOKEN.BANG          : ParseRule(self.unary,    None,        PREC.NONE),
            TOKEN.BANG_EQUAL    : ParseRule(None,          self.binary, PREC.EQUALITY),
            TOKEN.EQUAL         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.EQUAL_EQUAL   : ParseRule(None,          self.binary, PREC.EQUALITY),
            TOKEN.GREATER       : ParseRule(None,          self.binary, PREC.COMPARISON),
            TOKEN.GREATER_EQUAL : ParseRule(None,          self.binary, PREC.COMPARISON),
            TOKEN.LESS          : ParseRule(None,          self.binary, PREC.COMPARISON),
            TOKEN.LESS_EQUAL    : ParseRule(None,          self.binary, PREC.COMPARISON),
            TOKEN.IDENTIFIER    : ParseRule(self.variable, None,        PREC.NONE),
            TOKEN.STRING        : ParseRule(self.string,   None,        PREC.NONE),
            TOKEN.NUMBER        : ParseRule(self.number,   None,        PREC.NONE),
            TOKEN.AND           : ParseRule(None,          self.and_,   PREC.AND),
            TOKEN.CLASS         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.ELSE          : ParseRule(None,          None,        PREC.NONE),
            TOKEN.FALSE         : ParseRule(self.literal,  None,        PREC.NONE),
            TOKEN.FOR           : ParseRule(None,          None,        PREC.NONE),
            TOKEN.FUN           : ParseRule(None,          None,        PREC.NONE),
            TOKEN.IF            : ParseRule(None,          None,        PREC.NONE),
            TOKEN.NIL           : ParseRule(self.literal,  None,        PREC.NONE),
            TOKEN.OR            : ParseRule(None,          self.or_,    PREC.OR),
            TOKEN.PRINT         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.RETURN        : ParseRule(None,          None,        PREC.NONE),
            TOKEN.SUPER         : ParseRule(self.super,    None,        PREC.NONE),
            TOKEN.THIS          : ParseRule(self.this,     None,        PREC.NONE),
            TOKEN.TRUE          : ParseRule(self.literal,  None,        PREC.NONE),
            TOKEN.VAR           : ParseRule(None,          None,        PREC.NONE),
            TOKEN.WHILE         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.ERROR         : ParseRule(None,          None,        PREC.NONE),
            TOKEN.EOF           : ParseRule(None,          None,        PREC.NONE),
        }

    def currentChunk(self):
        return self.function.chunk

    def emitByte(self, byte: uint8_t):
        self.currentChunk().write(byte, self.parser.previous.line)

    def emitBytes(self, byte1: uint8_t, byte2: uint8_t):
        self.emitByte(byte1)
        self.emitByte(byte2)

    def emitReturn(self):
        if self.type == TYPE.INITIALIZER:
            self.emitBytes(OP.GET_LOCAL, 0)
        else:
            self.emitByte(OP.NIL)

        self.emitByte(OP.RETURN)

    def emitJump(self, instruction: uint8_t):
        self.emitByte(instruction)
        self.emitBytes(255, 255)
        return len(self.currentChunk().code) - 2

    def emitLoop(self, loopStart: int):
        self.emitByte(OP.LOOP)

        offset = len(self.currentChunk().code) - loopStart + 2
        if offset > UINT16_MAX: self.parser.error("Loop body too large.")

        self.emitByte((offset >> 8) & 0xff)
        self.emitByte(offset & 0xff)

    def patchJump(self, offset: int):
        # -2 to adjust for the bytecode for the jump offset itself.
        jump = len(self.currentChunk().code) - offset - 2

        if jump > UINT16_MAX:
            self.parser.error("Too much code to jump over.")

        self.currentChunk().code[offset] = (jump >> 8) & 0xff
        self.currentChunk().code[offset + 1] = jump & 0xff

    def makeConstant(self, value: Value):
        constant = self.currentChunk().addConstant(value)
        if constant > UINT8_MAX:
            self.parser.error("Too many constants in one chunk.")
            return 0

        return constant

    def emitConstant(self, value: Value):
        self.emitBytes(OP.CONSTANT, self.makeConstant(value))

    def identifierConstant(self, name: Token):
        return self.makeConstant(Value.from_obj(ObjString(name.source)))

    def parseVariable(self, errorMessage: str):
        self.parser.consume(TOKEN.IDENTIFIER, errorMessage)

        self.declareVariable()
        if self.scopeDepth > 0: return 0

        return self.identifierConstant(self.parser.previous)

    def declareVariable(self):
        if self.scopeDepth == 0: return

        name = self.parser.previous
        for local in reversed(self.locals):
            if local.depth != -1 and local.depth < self.scopeDepth:
                break

            if name.source == local.name.source:
                self.parser.error("Already a variable with this name in this scope.")

        self.addLocal(name)

    def addLocal(self, name: Token):
        if len(self.locals) == UINT8_COUNT:
            self.parser.error("Too many local variables in function.")
            return

        local = Local(name, -1, False)
        self.locals.append(local)

    def markInitialized(self):
        if self.scopeDepth == 0: return
        self.locals[-1].depth = self.scopeDepth

    def defineVariable(self, global_: uint8_t):
        if self.scopeDepth > 0:
            self.markInitialized()
            return

        self.emitBytes(OP.DEFINE_GLOBAL, global_)

    def resolveLocal(self, name: Token):
        for i,local in reversed(tuple(enumerate(self.locals))):
            if name.source == local.name.source:
                if local.depth == -1:
                    self.parser.error("Can't read local variable in its own initializer.")
                return i

        return -1

    def addUpvalue(self, index: uint8_t, isLocal: bool):
        for i,upvalue in enumerate(self.upvalues):
            if upvalue.index == index and upvalue.isLocal == isLocal:
                return i

        if len(self.upvalues) == UINT8_COUNT:
            self.parser.error("Too many closure variables in function.")
            return 0

        self.upvalues.append(Upvalue(index, isLocal))
        self.function.upvalueCount += 1
        return self.function.upvalueCount - 1

    def resolveUpvalue(self, name: Token):
        if self.enclosing is None: return -1

        local = self.enclosing.resolveLocal(name)
        if local != -1:
            self.enclosing.locals[local].isCaptured = True
            return self.addUpvalue(local, True)

        upvalue = self.enclosing.resolveUpvalue(name)
        if upvalue != -1:
            return self.addUpvalue(upvalue, False)

        return -1

    def namedVariable(self, name: Token, canAssign: bool):
        arg = self.resolveLocal(name)
        if arg != -1:
            getOp = OP.GET_LOCAL
            setOp = OP.SET_LOCAL
        elif (arg := self.resolveUpvalue(name)) != -1:
            getOp = OP.GET_UPVALUE
            setOp = OP.SET_UPVALUE
        else:
            arg = self.identifierConstant(name)
            getOp = OP.GET_GLOBAL
            setOp = OP.SET_GLOBAL

        if canAssign and self.parser.match(TOKEN.EQUAL):
            self.expression()
            self.emitBytes(setOp, arg)
        else:
            self.emitBytes(getOp, arg)

    def variable(self, canAssign: bool):
        self.namedVariable(self.parser.previous, canAssign)

    def this(self, canAssign: bool):
        if self.currentClass is None:
            self.parser.error("Can't use 'this' outside of a class.")
            return

        self.variable(False)

    def super(self, canAssign: bool):
        if self.currentClass is None:
            self.parser.error("Can't use 'super' outside of a class.")
        elif not self.currentClass.hasSuperclass:
            self.parser.error("Can't use 'super' in a class with no superclass.")

        self.parser.consume(TOKEN.DOT, "Expect '.' after 'super'.")
        self.parser.consume(TOKEN.IDENTIFIER, "Expect superclass method name.")
        name = self.identifierConstant(self.parser.previous)

        self.namedVariable(Token.synthetic("this"), False)
        if self.parser.match(TOKEN.LEFT_PAREN):
            argCount = self.argumentList()&0xff
            self.namedVariable(Token.synthetic("super"), False)
            self.emitBytes(OP.SUPER_INVOKE, name)
            self.emitByte(argCount)
        else:
            self.namedVariable(Token.synthetic("super"), False)
            self.emitBytes(OP.GET_SUPER, name)

    def end(self):
        self.emitReturn()

        if DEBUG_PRINT_CODE:
            if not self.parser.hadError:
                disassembleChunk(self.currentChunk(), str(self.function))

        return self.function

    def beginScope(self):
        self.scopeDepth += 1

    def endScope(self):
        self.scopeDepth -= 1

        for i in range(len(self.locals),0,-1):
            if self.locals[i - 1].depth <= self.scopeDepth:
                break
            if self.locals[-1].isCaptured:
                self.emitByte(OP.CLOSE_UPVALUE)
            else:
                self.emitByte(OP.POP)
            self.locals.pop()

    def getRule(self, type: TOKEN):
        return self.rules[type]

    def grouping(self, canAssign: bool):
        self.expression()
        self.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after expression.")

    def argumentList(self):
        argCount = 0
        if not self.parser.check(TOKEN.RIGHT_PAREN):
            _t = True
            while _t:
                self.expression()
                if argCount >= 255:
                    self.parser.error("Can't have more than 255 arguments.")
                argCount += 1
                _t = self.parser.match(TOKEN.COMMA)
        self.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after arguments.")
        return argCount

    def call(self, canAssign: bool):
        argCount = self.argumentList()&0xff
        self.emitBytes(OP.CALL, argCount)

    def dot(self, canAssign: bool):
        self.parser.consume(TOKEN.IDENTIFIER, "Expect property name after '.'.")
        name = self.identifierConstant(self.parser.previous)

        if canAssign and self.parser.match(TOKEN.EQUAL):
            self.expression()
            self.emitBytes(OP.SET_PROPERTY, name)
        elif self.parser.match(TOKEN.LEFT_PAREN):
            argCount = self.argumentList()&0xff
            self.emitBytes(OP.INVOKE, name)
            self.emitByte(argCount)
        else:
            self.emitBytes(OP.GET_PROPERTY, name)

    def number(self, canAssign: bool):
        value = float(self.parser.previous.source)
        self.emitConstant(Value.from_float(value))

    def string(self, canAssign: bool):
        self.emitConstant(Value.from_obj(ObjString(self.parser.previous.source[1:-1])))

    def unary(self, canAssign: bool):
        operatorType = self.parser.previous.type

        # Compile the operand.
        self.parsePrecedence(PREC.UNARY)

        # Emit the operator instruction.
        match operatorType:
            case TOKEN.BANG: self.emitByte(OP.NOT)
            case TOKEN.MINUS: self.emitByte(OP.NEGATE)
            case _: return # Unreachable.

    def binary(self, canAssign: bool):
        operatorType = self.parser.previous.type
        rule = self.getRule(operatorType)
        self.parsePrecedence(PREC(rule.precedence + 1))

        match operatorType:
            case TOKEN.BANG_EQUAL:    self.emitBytes(OP.EQUAL, OP.NOT)
            case TOKEN.EQUAL_EQUAL:   self.emitByte(OP.EQUAL)
            case TOKEN.GREATER:       self.emitByte(OP.GREATER)
            case TOKEN.GREATER_EQUAL: self.emitBytes(OP.LESS, OP.NOT)
            case TOKEN.LESS:          self.emitByte(OP.LESS)
            case TOKEN.LESS_EQUAL:    self.emitBytes(OP.GREATER, OP.NOT)
            case TOKEN.PLUS:          self.emitByte(OP.ADD)
            case TOKEN.MINUS:         self.emitByte(OP.SUBTRACT)
            case TOKEN.STAR:          self.emitByte(OP.MULTIPLY)
            case TOKEN.SLASH:         self.emitByte(OP.DIVIDE)
            case _: return # Unreachable

    def and_(self, canAssign: bool):
        endJump = self.emitJump(OP.JUMP_IF_FALSE)

        self.emitByte(OP.POP)
        self.parsePrecedence(PREC.AND)

        self.patchJump(endJump)

    def or_(self, canAssign: bool):
        elseJump = self.emitJump(OP.JUMP_IF_FALSE)
        endJump = self.emitJump(OP.JUMP)

        self.patchJump(elseJump)
        self.emitByte(OP.POP)

        self.parsePrecedence(PREC.OR)
        self.patchJump(endJump)

    def literal(self, canAssign: bool):
        match self.parser.previous.type:
            case TOKEN.FALSE: self.emitByte(OP.FALSE)
            case TOKEN.NIL: self.emitByte(OP.NIL)
            case TOKEN.TRUE: self.emitByte(OP.TRUE)
            case _: return # Unreachable

    def parsePrecedence(self, precedence: PREC):
        self.parser.advance()
        prefixRule = self.getRule(self.parser.previous.type).prefix
        if prefixRule is None:
            self.parser.error("Expect expression.")
            return

        canAssign = precedence <= PREC.ASSIGNMENT
        prefixRule(canAssign)

        while precedence <= self.getRule(self.parser.current.type).precedence:
            self.parser.advance()
            infixRule = self.getRule(self.parser.previous.type).infix
            infixRule(canAssign)

        if canAssign and self.parser.match(TOKEN.EQUAL):
            self.parser.error("Invalid assignment target.")

    def expression(self):
        self.parsePrecedence(PREC.ASSIGNMENT)

    def printStatement(self):
        self.expression()
        self.parser.consume(TOKEN.SEMICOLON, "Expect ';' after value.")
        self.emitByte(OP.PRINT)

    def forStatement(self):
        self.beginScope()
        self.parser.consume(TOKEN.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.parser.match(TOKEN.SEMICOLON):
            pass # No initializer.
        elif self.parser.match(TOKEN.VAR):
            self.varDeclaration()
        else:
            self.expressionStatement()

        loopStart = len(self.currentChunk().code)
        exitJump = -1
        if not self.parser.match(TOKEN.SEMICOLON):
            self.expression()
            self.parser.consume(TOKEN.SEMICOLON, "Expect ';' after loop condition.")

            # Jump out of the loop if the condition is false.
            exitJump = self.emitJump(OP.JUMP_IF_FALSE)
            self.emitByte(OP.POP) # Condition

        if not self.parser.match(TOKEN.RIGHT_PAREN):
            bodyJump = self.emitJump(OP.JUMP)
            incrementStart = len(self.currentChunk().code)
            self.expression()
            self.emitByte(OP.POP)
            self.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after for clauses.")

            self.emitLoop(loopStart)
            loopStart = incrementStart
            self.patchJump(bodyJump)

        self.statement()
        self.emitLoop(loopStart)

        if exitJump != -1:
            self.patchJump(exitJump)
            self.emitByte(OP.POP) # Condition

        self.endScope()

    def ifStatement(self):
        self.parser.consume(TOKEN.LEFT_PAREN, "Expect '(' after 'if'.")
        self.expression()
        self.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after condition.")

        thenJump = self.emitJump(OP.JUMP_IF_FALSE)
        self.emitByte(OP.POP)
        self.statement()

        elseJump = self.emitJump(OP.JUMP)

        self.patchJump(thenJump)
        self.emitByte(OP.POP)

        if self.parser.match(TOKEN.ELSE): self.statement()
        self.patchJump(elseJump)

    def returnStatement(self):
        if self.type == TYPE.SCRIPT:
            self.parser.error("Can't return from top-level code.")

        if self.parser.match(TOKEN.SEMICOLON):
            self.emitReturn()
        else:
            if self.type == TYPE.INITIALIZER:
                self.parser.error("Can't return a value from an initializer.")

            self.expression()
            self.parser.consume(TOKEN.SEMICOLON, "Expect ';' after return value.")
            self.emitByte(OP.RETURN)

    def whileStatement(self):
        loopStart = len(self.currentChunk().code)
        self.parser.consume(TOKEN.LEFT_PAREN, "Expect '(' after 'while'.")
        self.expression()
        self.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after condition.")

        exitJump = self.emitJump(OP.JUMP_IF_FALSE)
        self.emitByte(OP.POP)
        self.statement()
        self.emitLoop(loopStart)

        self.patchJump(exitJump)
        self.emitByte(OP.POP)

    def block(self):
        while (not self.parser.check(TOKEN.RIGHT_BRACE) and
               not self.parser.check(TOKEN.EOF)):
            self.declaration()

        self.parser.consume(TOKEN.RIGHT_BRACE, "Expect '}' after block.")

    def expressionStatement(self):
        self.expression()
        self.parser.consume(TOKEN.SEMICOLON, "Expect ';' after expression.")
        self.emitByte(OP.POP)

    def statement(self):
        if self.parser.match(TOKEN.PRINT):
            self.printStatement()
        elif self.parser.match(TOKEN.FOR):
            self.forStatement()
        elif self.parser.match(TOKEN.IF):
            self.ifStatement()
        elif self.parser.match(TOKEN.RETURN):
            self.returnStatement()
        elif self.parser.match(TOKEN.WHILE):
            self.whileStatement()
        elif self.parser.match(TOKEN.LEFT_BRACE):
            self.beginScope()
            self.block()
            self.endScope()
        else:
            self.expressionStatement()

    def method(self):
        self.parser.consume(TOKEN.IDENTIFIER, "Expect method name.")
        constant = self.identifierConstant(self.parser.previous)

        type = TYPE.METHOD
        if self.parser.previous.source == "init":
            type = TYPE.INITIALIZER

        self.function_(type)
        self.emitBytes(OP.METHOD, constant)

    def classDeclaration(self):
        self.parser.consume(TOKEN.IDENTIFIER, "Expect class name.")
        className = self.parser.previous
        nameConstant = self.identifierConstant(self.parser.previous)
        self.declareVariable()

        self.emitBytes(OP.CLASS, nameConstant)
        self.defineVariable(nameConstant)

        classCompiler = ClassCompiler()
        classCompiler.hasSuperclass = False
        classCompiler.enclosing = self.currentClass
        self.currentClass = classCompiler

        if self.parser.match(TOKEN.LESS):
            self.parser.consume(TOKEN.IDENTIFIER, "Expect superclass name.")
            self.variable(False)

            if className.source == self.parser.previous.source:
                self.parser.error("A class can't inherit from itself.")

            self.beginScope()
            self.addLocal(Token.synthetic("super"))
            self.defineVariable(0)

            self.namedVariable(className, False)
            self.emitByte(OP.INHERIT)
            classCompiler.hasSuperclass = True

        self.namedVariable(className, False)
        self.parser.consume(TOKEN.LEFT_BRACE, "Expect '{' before class body.")
        while (not self.parser.check(TOKEN.RIGHT_BRACE) and
               not self.parser.check(TOKEN.EOF)):
            self.method()
        self.parser.consume(TOKEN.RIGHT_BRACE, "Expect '}' after class body.")
        self.emitByte(OP.POP)

        if classCompiler.hasSuperclass:
            self.endScope()

        self.currentClass = self.currentClass.enclosing

    def function_(self, type: TYPE):
        compiler = Compiler(type, self, self.parser, self.scanner)
        compiler.function.chunk.__init__()
        compiler.beginScope()

        compiler.parser.consume(TOKEN.LEFT_PAREN, "Expect '(' after function name.")
        if not compiler.parser.check(TOKEN.RIGHT_PAREN):
            _t = True
            while _t:
                compiler.function.arity += 1
                if compiler.function.arity > 255:
                    compiler.parser.errorAtCurrent("Can't have more than 255 parameters.")
                constant = compiler.parseVariable("Expect parameter name.")
                compiler.defineVariable(constant)
                _t = compiler.parser.match(TOKEN.COMMA)
        compiler.parser.consume(TOKEN.RIGHT_PAREN, "Expect ')' after parameters.")
        compiler.parser.consume(TOKEN.LEFT_BRACE, "Expect '{' before function body.")
        compiler.block()

        function = compiler.end()
        self.emitBytes(OP.CLOSURE, self.makeConstant(Value.from_obj(function)))

        for upvalue in compiler.upvalues:
            self.emitBytes(int(upvalue.isLocal), upvalue.index)

    def funDeclaration(self):
        global_ = self.parseVariable("Expect function name.")
        self.markInitialized()
        self.function_(TYPE.FUNCTION)
        self.defineVariable(global_)

    def varDeclaration(self):
        global_ = self.parseVariable("Expect variable name.")

        if self.parser.match(TOKEN.EQUAL):
            self.expression()
        else:
            self.emitByte(OP.NIL)
        self.parser.consume(TOKEN.SEMICOLON,
                            "Expect ';' after variable declaration.")

        self.defineVariable(global_)

    def declaration(self):
        if self.parser.match(TOKEN.CLASS):
            self.classDeclaration()
        elif self.parser.match(TOKEN.FUN):
            self.funDeclaration()
        elif self.parser.match(TOKEN.VAR):
            self.varDeclaration()
        else:
            self.statement()

        if self.parser.panicMode: self.parser.synchronize()

    def compile(self, source: str):
        self.scanner.__init__(source)
        self.parser.__init__(self.scanner)
        self.function.chunk.__init__()

        self.parser.hadError = False
        self.parser.panicMode = False

        self.parser.advance()

        while not self.parser.match(TOKEN.EOF):
            self.declaration()

        function = self.end()
        return None if self.parser.hadError else function
