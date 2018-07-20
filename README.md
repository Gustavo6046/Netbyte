# Netbyte
**Byte code, rope flexibility with versatile networking.**

## About
Netbyte is a compiled intermediary language, with a compiler and virtual machine, written for Python.
It has a slightly Lisp-inspired syntax, with an Assembly/Batch-like statement flow logic,
and is quite flexible. Most of the things you can do in Python, you can do with binary
files and Netbyte.

Its flexibility comes from the fact it can store anything in two forms:

 * Python objects - Instruction, Operation, Function, etc.
 
 * Binary compiled code, the target of the compiler, **and** what the
   interpreter runs. This is what should be sent by sockets when sending
   instructions, not pickled Python objects.

It is not meant to be used as a direct language. Like Neko, it is meant to be
used as a compilation target, but, unlike Neko, the compiled binary code is
merely an architecture, so that you can make hierarchies out of it.

For example, we can have a Python dictionary; let's say it's just a 
list of functions used by specific objects (actors) or other functional
attributes and items of a network game, where each entry has a key
name, and its value is a list of Instructions, which compiled string —
`netbyte.Netbyte().compile(*instructions)` — can be transferred around
with TCP, and stored into other people's function lists using
`netbyte.Netbyte().read(binary_code)`, so that everyone knows what instructions
to run if a certain function X is called on an object `MyObject`.

For more examples, check the Programs folder.

## How to Use?

You will need Python 3 to be able to use Netbyte.

To set up the Standard Library directory, run:

    stdlibdir.bat

To compile, run:

    python compile.py input.nbc [output.nbe]
    
To execute, run:

    python main.py input.nbe [arguments - see Stdlib/args.nbc or Programs/printfile.nbc]
