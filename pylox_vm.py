"""
CPSC 323 Project 2 - Lox Bytecode Virtual Machine

This is a Python translation of the clox bytecode VM
architecture from Crafting Interpreters.

The structure follows the C version from the book:
- Chunk holds bytecode, constants, and line numbers.
- Opcodes are stored as small integer values.
- The VM uses an instruction pointer.
- The VM executes instructions with a fetch/decode/execute loop.
- Values are passed through a stack.
- The disassembler prints the flat bytecode instruction list.

Python lists are used instead of C dynamic arrays and Python dictionaries
are used where the C version would use hash tables.

Source:
Robert Nystrom, Crafting Interpreters, chapters 14-25
https://craftinginterpreters.com/contents.html
"""

from enum import IntEnum
from dataclasses import dataclass
import sys


class Op(IntEnum):
    CONSTANT = 1
    NIL = 2
    TRUE = 3
    FALSE = 4
    POP = 5
    GET_GLOBAL = 6
    DEFINE_GLOBAL = 7
    SET_GLOBAL = 8
    EQUAL = 9
    GREATER = 10
    LESS = 11
    ADD = 12
    SUBTRACT = 13
    MULTIPLY = 14
    DIVIDE = 15
    NOT = 16
    NEGATE = 17
    PRINT = 18
    JUMP = 19
    JUMP_IF_FALSE = 20
    LOOP = 21
    AND = 22
    OR = 23
    RETURN = 24


class Chunk:
    def __init__(self):
        self.code = []       # linear bytecode: list[int]
        self.constants = []  # constant pool
        self.lines = []

    def write(self, byte, line):
        self.code.append(byte)
        self.lines.append(line)

    def add_constant(self, value):
        self.constants.append(value)
        return len(self.constants) - 1


class StringInterner:
    def __init__(self):
        self.strings = {}

    def intern(self, text):
        if text not in self.strings:
            self.strings[text] = text
        return self.strings[text]


class VM:
    def __init__(self):
        self.stack = []
        self.globals = {}
        self.ip = 0

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            self.runtime_error("Stack underflow.")
        return self.stack.pop()

    def peek(self, distance=0):
        return self.stack[-1 - distance]

    def runtime_error(self, message):
        raise RuntimeError(message)

    def read_byte(self, chunk):
        byte = chunk.code[self.ip]
        self.ip += 1
        return byte

    def read_short(self, chunk):
        high = self.read_byte(chunk)
        low = self.read_byte(chunk)
        return (high << 8) | low

    def read_constant(self, chunk):
        return chunk.constants[self.read_byte(chunk)]

    def is_falsey(self, value):
        return value is None or value is False

    def run(self, chunk):
        self.ip = 0
        while True:
            instruction = Op(self.read_byte(chunk))

            if instruction == Op.CONSTANT:
                self.push(self.read_constant(chunk))

            elif instruction == Op.NIL:
                self.push(None)

            elif instruction == Op.TRUE:
                self.push(True)

            elif instruction == Op.FALSE:
                self.push(False)

            elif instruction == Op.POP:
                self.pop()

            elif instruction == Op.GET_GLOBAL:
                name = self.read_constant(chunk)
                if name not in self.globals:
                    self.runtime_error(f"Undefined variable '{name}'.")
                self.push(self.globals[name])

            elif instruction == Op.DEFINE_GLOBAL:
                name = self.read_constant(chunk)
                self.globals[name] = self.pop()

            elif instruction == Op.SET_GLOBAL:
                name = self.read_constant(chunk)
                if name not in self.globals:
                    self.runtime_error(f"Undefined variable '{name}'.")
                self.globals[name] = self.peek()

            elif instruction == Op.EQUAL:
                b = self.pop()
                a = self.pop()
                self.push(a == b)

            elif instruction == Op.GREATER:
                b = self.pop()
                a = self.pop()
                self.push(a > b)

            elif instruction == Op.LESS:
                b = self.pop()
                a = self.pop()
                self.push(a < b)

            elif instruction == Op.ADD:
                b = self.pop()
                a = self.pop()
                if isinstance(a, str) and isinstance(b, str):
                    self.push(a + b)
                elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    self.push(a + b)
                else:
                    self.runtime_error("Operands must be two numbers or two strings.")

            elif instruction == Op.SUBTRACT:
                b = self.pop()
                a = self.pop()
                self.push(a - b)

            elif instruction == Op.MULTIPLY:
                b = self.pop()
                a = self.pop()
                self.push(a * b)

            elif instruction == Op.DIVIDE:
                b = self.pop()
                a = self.pop()
                self.push(a / b)

            elif instruction == Op.NOT:
                self.push(self.is_falsey(self.pop()))

            elif instruction == Op.NEGATE:
                self.push(-self.pop())

            elif instruction == Op.AND:
                b = self.pop()
                a = self.pop()
                self.push((not self.is_falsey(a)) and (not self.is_falsey(b)))

            elif instruction == Op.OR:
                b = self.pop()
                a = self.pop()
                self.push((not self.is_falsey(a)) or (not self.is_falsey(b)))

            elif instruction == Op.PRINT:
                print(stringify(self.pop()))

            elif instruction == Op.JUMP:
                offset = self.read_short(chunk)
                self.ip += offset

            elif instruction == Op.JUMP_IF_FALSE:
                offset = self.read_short(chunk)
                if self.is_falsey(self.peek()):
                    self.ip += offset

            elif instruction == Op.LOOP:
                offset = self.read_short(chunk)
                self.ip -= offset

            elif instruction == Op.RETURN:
                return


def stringify(value):
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ---------------- scanner ----------------

class TokenType(IntEnum):
    LEFT_PAREN = 1; RIGHT_PAREN = 2
    LEFT_BRACE = 3; RIGHT_BRACE = 4
    COMMA = 5; DOT = 6; MINUS = 7; PLUS = 8
    SEMICOLON = 9; SLASH = 10; STAR = 11
    BANG = 12; BANG_EQUAL = 13
    EQUAL = 14; EQUAL_EQUAL = 15
    GREATER = 16; GREATER_EQUAL = 17
    LESS = 18; LESS_EQUAL = 19
    IDENTIFIER = 20; STRING = 21; NUMBER = 22
    AND = 23; ELSE = 24; FALSE = 25; IF = 26; NIL = 27
    OR = 28; PRINT = 29; TRUE = 30; VAR = 31; WHILE = 32
    EOF = 33


KEYWORDS = {
    "and": TokenType.AND,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: object
    line: int


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type_, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type_, text, literal, self.line))

    def match(self, expected):
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in ' \r\t':
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == '_':
            self.identifier()
        else:
            raise SyntaxError(f"Line {self.line}: unexpected character '{c}'")

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            raise SyntaxError(f"Line {self.line}: unterminated string")
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[self.start:self.current]
        self.add_token(KEYWORDS.get(text, TokenType.IDENTIFIER))


# ---------------- compiler ----------------

class Compiler:
    def __init__(self, tokens, interner):
        self.tokens = tokens
        self.current = 0
        self.chunk = Chunk()
        self.interner = interner

    def compile(self):
        while not self.check(TokenType.EOF):
            self.declaration()
        self.emit_byte(Op.RETURN)
        return self.chunk

    def declaration(self):
        if self.match(TokenType.VAR):
            self.var_declaration()
        else:
            self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        if self.match(TokenType.EQUAL):
            self.expression()
        else:
            self.emit_byte(Op.NIL)
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        self.emit_constant_instruction(Op.DEFINE_GLOBAL, self.interner.intern(name.lexeme))

    def statement(self):
        if self.match(TokenType.PRINT):
            self.print_statement()
        elif self.match(TokenType.IF):
            self.if_statement()
        elif self.match(TokenType.WHILE):
            self.while_statement()
        elif self.match(TokenType.LEFT_BRACE):
            self.block()
        else:
            self.expression_statement()

    def block(self):
        while not self.check(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            self.declaration()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")

    def print_statement(self):
        self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        self.emit_byte(Op.PRINT)

    def expression_statement(self):
        self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        self.emit_byte(Op.POP)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after if.")
        self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")

        then_jump = self.emit_jump(Op.JUMP_IF_FALSE)
        self.emit_byte(Op.POP)
        self.statement()

        else_jump = self.emit_jump(Op.JUMP)
        self.patch_jump(then_jump)
        self.emit_byte(Op.POP)

        if self.match(TokenType.ELSE):
            self.statement()
        self.patch_jump(else_jump)

    def while_statement(self):
        loop_start = len(self.chunk.code)
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after while.")
        self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")

        exit_jump = self.emit_jump(Op.JUMP_IF_FALSE)
        self.emit_byte(Op.POP)
        self.statement()
        self.emit_loop(loop_start)

        self.patch_jump(exit_jump)
        self.emit_byte(Op.POP)

    def expression(self):
        self.assignment()

    def assignment(self):
        if self.check(TokenType.IDENTIFIER) and self.check_next(TokenType.EQUAL):
            name = self.advance()
            self.advance()  # consume '='
            self.assignment()
            self.emit_constant_instruction(Op.SET_GLOBAL, self.interner.intern(name.lexeme))
        else:
            self.or_()

    def or_(self):
        self.and_()
        while self.match(TokenType.OR):
            self.and_()
            self.emit_byte(Op.OR)

    def and_(self):
        self.equality()
        while self.match(TokenType.AND):
            self.equality()
            self.emit_byte(Op.AND)

    def equality(self):
        self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous().type
            self.comparison()
            self.emit_byte(Op.EQUAL)
            if operator == TokenType.BANG_EQUAL:
                self.emit_byte(Op.NOT)

    def comparison(self):
        self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous().type
            self.term()
            if operator == TokenType.GREATER:
                self.emit_byte(Op.GREATER)
            elif operator == TokenType.GREATER_EQUAL:
                self.emit_byte(Op.LESS)
                self.emit_byte(Op.NOT)
            elif operator == TokenType.LESS:
                self.emit_byte(Op.LESS)
            elif operator == TokenType.LESS_EQUAL:
                self.emit_byte(Op.GREATER)
                self.emit_byte(Op.NOT)

    def term(self):
        self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous().type
            self.factor()
            self.emit_byte(Op.SUBTRACT if operator == TokenType.MINUS else Op.ADD)

    def factor(self):
        self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous().type
            self.unary()
            self.emit_byte(Op.DIVIDE if operator == TokenType.SLASH else Op.MULTIPLY)

    def unary(self):
        if self.match(TokenType.BANG):
            self.unary()
            self.emit_byte(Op.NOT)
        elif self.match(TokenType.MINUS):
            self.unary()
            self.emit_byte(Op.NEGATE)
        else:
            self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            self.emit_byte(Op.FALSE)
        elif self.match(TokenType.TRUE):
            self.emit_byte(Op.TRUE)
        elif self.match(TokenType.NIL):
            self.emit_byte(Op.NIL)
        elif self.match(TokenType.NUMBER):
            self.emit_constant(self.previous().literal)
        elif self.match(TokenType.STRING):
            self.emit_constant(self.interner.intern(self.previous().literal))
        elif self.match(TokenType.IDENTIFIER):
            self.emit_constant_instruction(Op.GET_GLOBAL, self.interner.intern(self.previous().lexeme))
        elif self.match(TokenType.LEFT_PAREN):
            self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
        else:
            raise SyntaxError(f"Line {self.peek().line}: Expected expression.")

    def emit_byte(self, byte):
        self.chunk.write(int(byte), self.previous().line if self.current > 0 else 1)

    def emit_bytes(self, *bytes_):
        for byte in bytes_:
            self.emit_byte(byte)

    def emit_constant(self, value):
        constant = self.make_constant(value)
        self.emit_bytes(Op.CONSTANT, constant)

    def emit_constant_instruction(self, op, value):
        constant = self.make_constant(value)
        self.emit_bytes(op, constant)

    def make_constant(self, value):
        index = self.chunk.add_constant(value)
        if index > 255:
            raise SyntaxError("Too many constants in one chunk.")
        return index

    def emit_jump(self, instruction):
        self.emit_bytes(instruction, 0xff, 0xff)
        return len(self.chunk.code) - 2

    def patch_jump(self, offset):
        jump = len(self.chunk.code) - offset - 2
        if jump > 65535:
            raise SyntaxError("Too much code to jump over.")
        self.chunk.code[offset] = (jump >> 8) & 0xff
        self.chunk.code[offset + 1] = jump & 0xff

    def emit_loop(self, loop_start):
        self.emit_byte(Op.LOOP)
        offset = len(self.chunk.code) - loop_start + 2
        if offset > 65535:
            raise SyntaxError("Loop body too large.")
        self.emit_byte((offset >> 8) & 0xff)
        self.emit_byte(offset & 0xff)

    def match(self, *types):
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def consume(self, type_, message):
        if self.check(type_):
            return self.advance()
        raise SyntaxError(f"Line {self.peek().line}: {message}")

    def check(self, type_):
        return self.peek().type == type_

    def check_next(self, type_):
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == type_

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]


# ---------------- disassembler ----------------

def disassemble_chunk(chunk, name="script"):
    print(f"== Disassembly: {name} ==")
    offset = 0
    while offset < len(chunk.code):
        offset = disassemble_instruction(chunk, offset)


def disassemble_instruction(chunk, offset):
    print(f"{offset:04d} ", end="")
    instruction = Op(chunk.code[offset])

    if instruction == Op.CONSTANT:
        return constant_instruction("OP_CONSTANT", chunk, offset)
    if instruction == Op.GET_GLOBAL:
        return constant_instruction("OP_GET_GLOBAL", chunk, offset)
    if instruction == Op.DEFINE_GLOBAL:
        return constant_instruction("OP_DEFINE_GLOBAL", chunk, offset)
    if instruction == Op.SET_GLOBAL:
        return constant_instruction("OP_SET_GLOBAL", chunk, offset)
    if instruction in (Op.JUMP, Op.JUMP_IF_FALSE):
        return jump_instruction(instruction.name, 1, chunk, offset)
    if instruction == Op.LOOP:
        return jump_instruction("LOOP", -1, chunk, offset)

    print("OP_" + instruction.name)
    return offset + 1


def constant_instruction(name, chunk, offset):
    constant = chunk.code[offset + 1]
    print(f"{name:<16} {constant:4d} '{stringify(chunk.constants[constant])}'")
    return offset + 2


def jump_instruction(name, sign, chunk, offset):
    jump = (chunk.code[offset + 1] << 8) | chunk.code[offset + 2]
    target = offset + 3 + sign * jump
    print(f"OP_{name:<13} {offset:4d} -> {target}")
    return offset + 3


# ---------------- front door ----------------

def compile_source(source):
    interner = StringInterner()
    tokens = Scanner(source).scan_tokens()
    return Compiler(tokens, interner).compile()


def run_source(source, debug=False, name="script"):
    chunk = compile_source(source)
    if debug:
        disassemble_chunk(chunk, name)
    else:
        VM().run(chunk)


def main(argv):
    debug = False
    files = []
    for arg in argv[1:]:
        if arg == "-d":
            debug = True
        else:
            files.append(arg)

    if not files:
        print("Usage: py pylox_vm.py [-d] file.lox")
        return 64

    filename = files[0]
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        run_source(source, debug, filename)
        return 0
    except (SyntaxError, RuntimeError) as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
