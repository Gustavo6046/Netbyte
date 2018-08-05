import netbyte
import sys

nbe = netbyte.Netbyte()

if sys.argv[1] == "-":
    open((sys.argv[2] if len(sys.argv) > 2 else sys.argv[1][:-1] + 'e'), "wb").write(nbe.compile(*nbe.parse(sys.stdin.read(), "STDIN"), debug=True))

else:
    open((sys.argv[2] if len(sys.argv) > 2 else sys.argv[1][:-1] + 'e'), "wb").write(nbe.compile(*nbe.parse_file(sys.argv[1]), debug=True))