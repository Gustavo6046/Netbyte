import netbyte
import sys

res = netbyte.Netbyte().execute_file(sys.argv[1] if len(sys.argv) > 1 else "test.nbe")

if res is not None:
    print("[The file returned '{}'.]".format(res))