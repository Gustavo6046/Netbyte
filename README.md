# Netbyte
**Byte code, rope flexibility in atomic volume.**

-----

For a demonstration of its capabilities, run:

    python main.py test.nbe
    
Such will run the bytecode file `test.nbe`, which weights just **83 bytes!** In that very space,
we can print the string "Hello!", the string "1234", and return the integer 30, adding three
10's Lisp-style.

And yes, the file has a return value, much like a function!

This code is equivalent to the Python:

    def main():
        print("Hello!")
        print("1234")
        return 10 + 10 + 10
        
    main()
    
And its expression chaining syntax, which makes this so flexible, is inspired by Lisp. See the
code, especially that at `netbyte.py`, to learn more about the opcodes (Operation Codes) and
expcodes (Expression Codes), and all the types too!

No compilers yet.