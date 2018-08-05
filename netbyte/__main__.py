#!/usr/bin/python
import sys
import textwrap
import netbyte


def compile():
    nbe = netbyte.Netbyte()

    if len(sys.argv) < 2:
        print("Please give as argument a filename (or '-' for the standard input)!")
        return 1

    if sys.argv[2] == "-":
        if len(sys.argv) < 3:
            print("Stdin compilation MUST specify a target bytecode filename.")
            return 1
    
        open(sys.argv[3], "wb").write(nbe.compile(*nbe.parse(sys.stdin.read(), "STDIN"), debug=True))

    else:
        open((sys.argv[3] if len(sys.argv) > 3 else sys.argv[2][:-1] + 'e'), "wb").write(nbe.compile(*nbe.parse_file(sys.argv[2]), debug=True))
        
def run():
    res = netbyte.Netbyte().execute((open(sys.argv[2], 'rb').read() if len(sys.argv) > 2 else sys.stdin.read()), (sys.argv[2] if len(sys.argv) > 2 else "<stdin>"))

    if res is not None:
        print("[File return value: '{}']".format(res))
        
commands = {
    'compile': compile,
    'run': run
}

descriptions = {
    'compile': ["Compile your Netbyte source code.", "Usage: compile (<source> [target] | - [target])"],
    'run': ["Run your newly-compiled Netbyte bytecode program files.", "Usage: run <target>"]
}

cmd = (sys.argv[1] if len(sys.argv) > 1 else None)

if cmd not in commands:
    if cmd is not None:
        print("Error: No such command '{}'!".format(cmd))
        print()
        
    print("Available subcommands:")
    
    for k, vl in descriptions.items():
        print("  - {}".format(k))
        
        for v in vl:
            for line in textwrap.wrap(v, 64):
                print(" " * 6 + line)
            
        print()
    
else:
    commands[cmd]()