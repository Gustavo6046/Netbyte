import interpreter
import sys

res = interpreter.Interpreter().execute_file(sys.argv[1] if len(sys.argv) > 1 else "test.nbe")
print("[The file returned '{}'.]".format(res))