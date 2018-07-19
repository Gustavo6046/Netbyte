# Netbyte
**Byte code, rope flexibility in atomic volume.**

-----

For a demonstration of its capabilities, run:

    python main.py test.nbe
    
Such will run the bytecode file `test.nbe`, which weights just **249 bytes!** In that very space,
we can print a few strings, and add 20 and 100 to an X variable several times, using function arguments.

And yes, the file has a return value, much like a function!

The code, before compiled: (`test.nbc`)

    SETVAR "X" null 0
    PRINTV "Testing...\n\n=======\n"

    MKFUNC "ABCD" null \
        {GSTVAR "X" null (ADDNUM X (GETARG 0))} \
        {PRINTV "Added" (GETARG 0) "to X! X is now:" X}
        
    NULLEV (REPEAT 50 ABCD(20))
    NULLEV (REPEAT 8 ABCD(100))
    RETURN X

is equivalent to the Python:

    def main():
        x = 0
    
        def ABCD(y):
            x += y
            print("Added {} to X! X is now {}".format(y, x))
    
        for _ in range(50):
            ABCD(20)
            
        for _ in range(8):
            ABCD(100)
            
        return x
        
    main()
    
And its expression chaining syntax, which makes this so flexible, is inspired by Lisp. See the
code, especially that at `netbyte.py`, to learn more about the opcodes (Operation Codes) and
expcodes (Expression Codes), and all the types too!

No compilers yet.