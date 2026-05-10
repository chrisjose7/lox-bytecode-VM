CPSC 323 Project 2 - Lox Bytecode Virtual Machine

This project is a Python translation of the C bytecode VM structure from Crafting Interpreters.
I used ChatGPT to help translate and simplify the Crafting Interpreters clox bytecode VM structure into Python, but I reviewed and tested the code myself.

The main design follows the book's clox architecture:
- Chunk stores bytecode, constants, and line information
- Opcodes are represented with an enum
- The VM uses an instruction pointer
- The VM executes bytecode using a fetch/decode/execute loop
- Values are passed through a stack
- The disassembler prints the flat bytecode instruction list

The Python version uses lists instead of manually allocated C arrays and dictionaries instead of C hash tables, but I kept the structure close to the book's VM design.

Source:
https://craftinginterpreters.com/contents.html

The project includes:
- Chunk structure for linear bytecode
- Opcodes
- Constant pool
- Stack-based VM execution
- Instruction pointer
- String interning
- Debug disassembler using the -d flag
- Support for arithmetic, comparisons, variables, assignment, print, if statements, and while loops

Run normally:
py pylox_vm.py example.lox

Run disassembler:
py pylox_vm.py -d example.lox