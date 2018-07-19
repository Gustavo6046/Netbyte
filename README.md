# Netbyte
**Byte code, rope flexibility in atomic volume.**

## About

For a demonstration of its capabilities, run:

    python main.py test.nbe
    
Such will run the bytecode file `test.nbe`, which weights just **908 bytes!** In that very space,
we can print a few strings, and add 20 and 100 to an X variable several times, using function arguments,
then verify if the result is larger than a set number (11000).

And yes, the file has a return value, much like a function!

The code, before compiled: (`test.nbc`)

    SETVAR "X" 0
    SETVAR "i" 0
    PRINTV "Testing...\n\n=======\n"

    MKFUNC "ABCD" null \
        {GSTVAR "X" (ADDNUM X (GETARG 0))} \
        {PRINTV "Added" (GETARG 0) "to X! X is now:" X}
        
    MLABEL "Loop"
    NULLEV (REPEAT 50 ABCD(20))
    NULLEV (REPEAT 30 ABCD(100))
    SETVAR "i" (ADDNUM i 1)
    PRINTV (CONCAT "--- Iteration #" i) "Finished ---"
    JUMPIF (LSRTHN X 10000) "Loop"
    NULLEV (IFELSE (LSRTHN X 11000) {PRINTV X "is smaller than 11000."} {PRINTV X "is greater than or equal to 11000."})
    RETURN X

is equivalent to the Python code below:

    def main():
        x = 0
        i = 0

        def ABCD(y):
            x += y
            print("Added {} to X! X is now {}".format(y, x))

        while x < 10000:
            for _ in range(50):
                ABCD(20)
                
            for _ in range(8):
                ABCD(100)
                
            i += 1
            print("--- Iteration #{} Finished ---".format(i))
        
        if x < 11000:
            print(x, "is smaller than 11000.")
            
        else:
            print(x, "is greater than or equal to 11000.")
        
        return x
        
    main()
    
which weights 536 bytes.
    
And its expression chaining, inspired by Lisp, is what makes this so flexible. See the
code, especially that at `netbyte.py`, to learn more about the opcodes (Operation Codes) and
expcodes (Expression Codes), and all the types too!

It's not meant to be used as a direct language, but rather as an intermediary step for a higher
level language, with a transpiler. Netbyte has this name because it was originally meant to be
used in network applications, with network abstractions, as a Java-like language would. Now,
it's a middle assembly language.

## How to Use?

You will need Python 3 to be able to use Netbyte. To compile, run:

    python compile.py input.nbc [output.nbe]
    
To execute, run:

    python main.py input.nbe
