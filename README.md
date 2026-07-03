# Lox Bytecode VM (Python)

A single-pass compiler and **stack-based bytecode virtual machine** for a subset
of the Lox language, following the `clox` architecture from Robert Nystrom's
*Crafting Interpreters* (chapters 14-25). Source is scanned, compiled to a flat
sequence of bytecode instructions, and executed by a fetch/decode/execute loop
over an operand stack.

This is the bytecode-VM counterpart to the tree-walk interpreter in
[Lox-Interpreter](https://github.com/chrisjose7/Lox-Interpreter).

## Features

- **Chunk** structure storing bytecode, a constant pool, and line information
- **Opcodes** as an `IntEnum`, dispatched in the VM's main loop
- **Stack-based execution** with an instruction pointer
- **Constant pool** with string interning
- **Control flow via jump opcodes** — `if`/`else` compiles to `JUMP_IF_FALSE`/`JUMP`; `while` uses a backward `LOOP` instruction
- **Debug disassembler** that prints the compiled bytecode
- Language support: arithmetic, comparisons (`< > == !=` etc.), `and`/`or`,
  global variables, assignment, `print`, `if`/`else`, and `while` loops

## Running

Run a program:
```bash
python pylox_vm.py example.lox
```

Print the compiled bytecode instead of running it:
```bash
python pylox_vm.py -d example.lox
```

## Example

`example.lox`:
```lox
var x = 0;

while (x < 3) {
  print x;
  x = x + 1;
}

if (x == 3) {
  print "done";
} else {
  print "bad";
}
```

Output:
```
0
1
2
done
```

Disassembly (`-d`) shows the compiled bytecode, including the loop and jumps:
```
0000 OP_CONSTANT         0 '0'
0002 OP_DEFINE_GLOBAL    1 'x'
0004 OP_GET_GLOBAL       2 'x'
0006 OP_CONSTANT         3 '3'
0008 OP_LESS
0009 OP_JUMP_IF_FALSE    9 -> 27
...
0024 OP_LOOP            24 -> 4
0027 OP_POP
...
0047 OP_RETURN
```

## Design notes

The implementation mirrors the book's `clox` design, adapted to Python:

- A **Chunk** holds the linear bytecode, a constant pool, and per-instruction
  line numbers.
- The **compiler** is single-pass: it scans tokens and emits bytecode directly
  using recursive-descent parsing with precedence (`term`, `factor`, `unary`,
  etc.), rather than building an AST first.
- **Control flow** is compiled to jumps. Forward jumps (`if`, loop exit) are
  emitted with a placeholder operand that is back-patched once the jump target
  is known; `while` emits a backward `LOOP` instruction.
- The **VM** runs a fetch/decode/execute loop, pushing and popping values on an
  operand stack and tracking position with an instruction pointer.

Where `clox` uses manually allocated C arrays and hash tables, this version uses
Python lists and dictionaries while keeping the structure close to the book's.

## Repository layout

| File | Purpose |
|------|---------|
| `pylox_vm.py` | Scanner, single-pass compiler, disassembler, and stack-based VM |
| `example.lox` | Sample program exercising variables, a `while` loop, and `if`/`else` |
| `tests/` | Sample programs: `arithmetic_variables.lox`, `strings.lox` |

## Scope and limitations

This covers the expression, global-variable, and control-flow chapters of the
book. It does **not** include local variables/scoping, functions/calls, closures,
or classes (later `clox` chapters). It is a learning implementation focused on
the compile-to-bytecode and VM-execution pipeline.

## Acknowledgements

Based on the `clox` bytecode VM from *Crafting Interpreters* by Robert Nystrom
(https://craftinginterpreters.com). I used ChatGPT to help translate the book's
C structures into Python, and reviewed and tested the implementation myself.
