import time
import warnings
import struct
import re
import math
import sys
import importlib

from functools import reduce
# from socket import socket, AF_INET, SOCK_STREAM, error as SocketError

# Note that optional arguments default to None (Python) or NULLVL (Netbyte).

# Base Operations
BASE_OPCODES = [
    "SETVAR", # Set Variable : string name, string scope, any value
    "GSTVAR", # Global Set Variable : string name, any value
    "DELVAR", # Delete Variable : string name
    "MKFUNC", # Make Function : string name, byte string expressions, optional string scope
    "RETURN", # Set return value
    "TERMIN", # Terminate
    "JUMPIF", # Jump If instruction, with condition and position...
    "JUMPIN", # Jump If Not instruction, with condition and position...
    "JUMPTO", # Jump To instruction at position...
    "JUMPLB", # Jump to Label
    "MLABEL", # Mark Label
    "EXFILE", # Execute File
    "PRINTV", # Print Value
    "NULLEV", # Null Evaluation: for executing functions without printing their result!
]

# Expression Types
TYPES = [
    "NULLVL", # Null Value
    "ITNUMS", # Signed Integer Number
    "ITNUMU", # Unsigned Integer Number
    "FLTNUM", # Floating Point Number
    "DBLNUM", # Double Floating Point Number
    "STRING", # String
    "RTINST", # Instruction
    "BOOLTF", # Boolean True/False
    "VARRAY", # Value Array
]

# Expression Operators
EXPR_OPCODES = [
    # Generic Operators
    "GETVAR", # Retrieve Variable : string name, string scope -> any
    "VTOSTR", # String Conversion : any -> string
    "GETARG", # Get function Argument from index : int -> any
    "REPEAT", # Repeat expression multiple times (for function calls)
    "FNCALL", # Function Call : string (name), optional string (scope), 0+ anything -> anything
    "NFCALL", # Native Function Call : string (name), string (module), 0+ anything (no kwargs) -> anything
    "CHRONO", # Time : optional double offset -> double Unix time
    
    # Comparison Operators
    "EQUALS", # Equation : 2+ any -> bool
    "DIFFER", # Differentiation : 2+ any -> bool
    
    # Boolean Logic Operators
    "LOGAND", # Logic AND : 2+ bool -> bool
    "LOGIOR", # Logic OR : 2+ bool -> bool
    "LOGXOR", # Logic XOR : 2+ bool -> bool
    "LOGNOT", # Logic NOT : bool -> bool
    
    # Numeric Operators
    "ADDNUM", # Addition : 2+ numbers -> number
    "SUBNUM", # Subtraction : 2 numbers -> number
    "MULNUM", # Multiplication : 2+ numbers -> number
    "DIVNUM", # Division : 2 numbers -> number
    "POWNUM", # Power : 2 numbers -> number
    "ROTNUM", # Root Root : 2 number -> number
    "ANDNUM", # Bitwise AND : 2+ numbers -> number
    "IORNUM", # Bitwise OR : 2+ numbers -> number
    "XORNUM", # Bitwise XOR : 2+ numbers -> number
    "NOTNUM", # Bitwise NOT : 2+ numbers -> number
    
    # String Operators
    "SSLICE", # String Slice : string, 2 numbers -> string
    "CONCAT", # Concatenation : 2+ strings -> string
    "SPSCHR", # Char at Position : string, number -> string [length 1]
]

def exvalue(expr, *args, **kwargs):
    return expr.__value__(*args, **kwargs)
        
def dbgvalue(expr):
    return expr.__debug_value__()
        
class Expression(object):
    def __value__(self):
        raise RuntimeError("Expression objects can't be used directly!")
        
class Operation(Expression):
    def __init__(self, environment, operator, *args, scope=None, function=None):
        self.environment = environment
        self.operator = operator
        self.operands = args
        self.scope = scope
        self.function = function
        
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return "[{} operation with {} operands]".format(self.operator, len(self.operands))
        
    def __debug_value__(self):
        return self.operator, tuple(map(dbgvalue, self.operands))
        
    def __value__(self):
        # print(self.operator, self.operands)
        
        if self.operator == "REPEAT":
            res = None            
        
            for _ in range(exvalue(self.operands[0])):
                res = exvalue(self.operands[1])
                
            return res
            
        operands = tuple(map(exvalue, self.operands))
        
        # print(self.operator, "has operands", operands, "derived from", tuple(map(dbgvalue, self.operands)))
    
        if self.operator == "VTOSTR":
            return str(operands[0])
    
        if self.operator == "GETVAR":
            return self.environment.variables[operands[1] if operands[1] is not None else ''][operands[0]]
    
        if self.operator == "EQUALS":
            return len(set(operands)) < 2
            
        if self.operator == "DIFFER":
            return len(set(operands)) > 1
    
        if self.operator == "CHRONO":
            return time.time() + (operands[0] if len(operands) > 0 else 0)
        
        if self.operator == "ADDNUM":
            return sum(operands)
            
        if self.operator == "SUBNUM":
            return operands[0] - operands[1]
            
        if self.operator == "MULNUM":
            return reduce(lambda a, b: a * b, operands, 1)
            
        if self.operator == "DIVNUM":
            return operands[0] / operands[1]
            
        if self.operator == "POWNUM":
            return math.pow(operands[0], operands[1])
            
        if self.operator == "ROTNUM":
            return math.pow(operands[0], 1.0 / operands[1])
            
        if self.operator == "ANDNUM":
            return reduce(lambda a, b: a & b, operands)
            
        if self.operator == "IORNUM":
            return reduce(lambda a, b: a | b, operands)
            
        if self.operator == "XORNUM":
            return reduce(lambda a, b: a ^ b, operands)
            
        if self.operator == "NOTNUM":
            return ~operands[0]
            
        if self.operator == "LOGAND":
            return reduce(lambda a, b: a and b, operands)
            
        if self.operator == "LOGIOR":
            return reduce(lambda a, b: a or b, operands)
            
        if self.operator == "LOGXOR":
            return reduce(lambda a, b: bool(a) != bool(b), operands)
            
        if self.operator == "LOGNOT":
            return not operands[0]
            
        if self.operator == "SSLICE":
            return operands[0][operands[1]: operands[2]]
            
        if self.operator == "CONCAT":
            return reduce(lambda a, b: "{}{}".format(a, b), operands, '')
            
        if self.operator == "SPSCHR":
            return operands[0][operands[1]]
            
        if self.operator == "FNCALL":
            return self.environment.functions[operands[1] if operands[1] is not None else ''][operands[0]].execute(*operands[2:])
            
        if self.operator == "GETARG":
            if self.function is None:
                return 0
                
            else:
                return self.function._args[operands[0]]
            
        if self.operator == "NFCALL":
            return getattr(importlib.import_module(operands[1]), operands[0])(operands[2:])
        
class Literal(Expression):
    def __init__(self, environment, value):
        self.environment = environment
        self.value = value
        
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return repr(self.value)

    def __debug_value__(self):
        return self.value
        
    def __value__(self):
        return self.value

class Function(object):
    def __init__(self, environment, scope, name, *instructions):
        self.environment = environment
        self.scope = scope
        self.name = name
        self.instructions = instructions
        
    def __hash__(self):
        return hash(self.scope.replace(':', '_') + "::" + self.name.replace(':', '_'))
        
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return "[Function with {} instructions]".format(len(self.instructions))
        
    def execute(self, *args):
        res = None
        labels = {}
        pos = 0
        self._args = args
        
        while pos < len(self.instructions):
            i = self.instructions[pos]
            status = i.execute()
            
            if status is not None:
                if status == "SETRES":
                    res = self.environment.return_stack[self]
                    self.environment.return_stack[self] = None
                    
                elif status == "TERMINATE":
                    break
                    
                elif status[:5] == "JUMP:":
                    pos = int(status[5:])
                    
                elif status[:6] == "LJUMP:":
                    pos = labels[status[6:]]
                    
                elif status[:6] == "LABEL:":
                    labels[status.split(':')[1]] = pos + 1
                    pos = int(status.split(':')[2])
                    
            if status is None or (status[:5] != "JUMP:" and status[:6] != "LJUMP:"):
                pos += 1
                
        return res
        
class Instruction(object):
    def __init__(self, environment, scope, opcode, *args, function=None):
        self.environment = environment
        self.scope = scope
        self.opcode = opcode
        self.arguments = args
        self.function = function
        
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return "[{} instruction]".format(self.opcode)
        
    def __debug_value__(self):
        return self.opcode, tuple(map(dbgvalue, self.arguments))
        
    def execute(self):
        arguments = tuple(map(exvalue, self.arguments))
        
        # print(self.opcode, "has arguments", arguments, "derived from", tuple(map(dbgvalue, self.arguments)))
    
        if self.opcode == 'SETVAR':
            sc = (self.scope + ":" if self.scope is not None else "") + (arguments[1] if arguments[1] is not None else "")
        
            if sc not in self.environment.variables:
                self.environment.variables[sc] = {}
            
            self.environment.variables[sc][arguments[0]] = arguments[2]
            
        if self.opcode == 'GSTVAR':
            sc = ""
        
            if sc not in self.environment.variables:
                self.environment.variables[sc] = {}
        
            self.environment.variables[sc][arguments[0]] = arguments[2]
            
        elif self.opcode == 'DELVAR':
            if self.scope in self.environment.variables and arguments[0] in self.environment.variables[self.scope]:
                self.environment.variables[self.scope].pop(arguments[0])
                
        elif self.opcode == 'MKFUNC':
            name = arguments[0]
            scope = (self.scope + ":" if self.scope is not None else "") + (arguments[1] if arguments[1] is not None else "")
            instructions = arguments[2:]
            
            if scope is not None:
                for i in instructions:
                    i.scope = scope
            
            if scope not in self.environment.functions:
                self.environment.functions[scope] = {}
            
            f = Function(self.environment, scope, name, *instructions)
            self.environment.functions[scope][name] = f
            
            def set_function(ioo):
                if type(ioo) is Operation:
                    ioo.function = (ioo.function if ioo.function is not None else f)
                
                    for o in ioo.operands:
                        set_function(o)
                        
                elif type(ioo) is Instruction:
                    ioo.function = (ioo.function if ioo.function is not None else f)
                
                    for o in ioo.arguments:
                        set_function(o)
                
            for i in instructions:
                set_function(i)
            
        elif self.opcode == "RETURN":
            if self.function:
                self.environment.return_stack[self.function] = arguments[0]
                
            else:
                self.environment.last_return = arguments[0]
                
            return "SETRES"
            
        elif self.opcode == "TERMIN":
            return "TERMINATE"
            
        elif self.opcode == "JUMPIF":
            if arguments[0]:
                return "JUMP:" + str(arguments[1])
            
        elif self.opcode == "JUMPIN":
            if not arguments[0]:
                return "JUMP:" + str(arguments[1])
            
        elif self.opcode == "CALLIF":
            if arguments[0]:
                return "JUMP:" + str(arguments[1])
            
        elif self.opcode == "JUMPTO":
            return "JUMP:" + str(arguments[0])
            
        elif self.opcode == "MLABEL":
            return "LABEL:{}:{}".format(arguments[0], arguments[1])
            
        elif self.opcode == "JUMPLB":
            return "LJUMP:" + arguments[0]
            
        elif self.opcode == "EXFILE":
            self.environment.execute(open(self.arguments[0], 'rb').read())
                        
        elif self.opcode == "PRINTV":
            if self.environment.pstream is sys.stdout or self.environment.pstream is sys.stderr:
                self.environment.pstream.write(" ".join(tuple(map(str, arguments))) + "\n")
            
            else:
                self.environment.pstream.write(bytes(" ".join(tuple(map(str, arguments))), 'utf-8') + b"\n")
            
        elif self.opcode == "NULLEV":
            return # we already evaluated the arguments anyway :P
            
    def __value__(self):
        return self
        
class VersionCheckError(BaseException):
    def __init__(self, msg):
        self.msg = msg
        
class Netbyte(object):
    VERSION = "0.0.5"

    def __init__(self, print_stream=sys.stdout):
        self.variables = {}
        self.functions = {}
        self.return_stack = {}
        self.files = []
        self.pstream = print_stream
        self.last_return = None
        
    def _get_str(self, data, pos):
        length = struct.unpack("=I", data[pos: pos + 4])[0]
        sd = data[pos + 4: pos + 4 + length]
        return sd.decode('utf-8')
        
    def read_literal(self, data, pos, scope=None, absolute_pos=None, superlen=None):
        if absolute_pos is None:
            absolute_pos = pos
        
        length = struct.unpack("=L", data[pos: pos + 4])[0]
        sd = data[pos + 4:pos + 5 + length]
        ltype = TYPES[data[pos + 4]]
        sd = sd[1:]
        
        if ltype == "NULLVL":
            # print(">", ltype, length, superlen, "@", hex(absolute_pos))
            return Literal(self, None)
            
        elif ltype == "ITNUMS":
            fmts = {
                1: "b",
                2: "h",
                4: "i",
                8: "q"
            }
        
            return Literal(self, struct.unpack("=" + fmts[len(sd)], sd)[0])
            
        elif ltype == "ITNUMU":
            fmts = {
                1: "B",
                2: "H",
                4: "I",
                8: "Q"
            }
        
            return Literal(self, struct.unpack("=" + fmts[len(sd)], sd)[0])
            
        elif ltype == "FLTNUM":
            # print(">", ltype, length, superlen, struct.unpack("=f", sd[:4])[0], "@", hex(absolute_pos))
            return Literal(self, struct.unpack("=f", sd[:4])[0])
            
        elif ltype == "DBLNUM":
            # print(">", ltype, length, superlen, struct.unpack("=d", sd[:8])[0], "@", hex(absolute_pos))
            return Literal(self, struct.unpack("=d", sd[:8])[0])
            
        elif ltype == "STRING":
            # print(">", ltype, length, superlen, repr(sd.decode('utf-8')), "@", hex(absolute_pos))
            return Literal(self, sd.decode('utf-8'))
            
        elif ltype == "RTINST":
            # print(">", ltype, length, superlen, "@", hex(absolute_pos))
            return self.read_instruction(sd, 0, scope, absolute_pos=absolute_pos + 5)[1]
            
        elif ltype == "BOOLTF":
            return Literal(self, sd[0] > 0)
            
        elif ltype == "VARRAY":
            res = []
            leng2 = struct.unpack("=L", sd[:4])
            ad = sd[4:]
            
            while len(ad) > 4:
                sublen = struct.unpack("=L", ad[:4])
                ad = ad[4:]
                res.append(read_expression(ad[:sublen]))
                ad = ad[sublen:]
            
            return Literal(self, res)
        
    def read_expression(self, data, pos, scope=None, absolute_pos=None, level=0, function=None):
        length = struct.unpack("=L", data[pos: pos + 4])[0]
        
        if length == 0:
            # assume NULLVL (null value)
            return 4, None
        
        # print(hex(absolute_pos if absolute_pos is not None else pos), length, "L" + str(level))
        expr = data[pos + 4: pos + 4 + length]
        
        # print(absolute_pos, length, expr[0])
        
        if expr[0] > 0:
            operator = EXPR_OPCODES[expr[0] - 1]
            # print(operator)
            # print(">", hex((absolute_pos if absolute_pos is not None else pos) + 3), expr[0], operator)
            rpos = 0
            arguments = []
            
            while rpos + 1 < len(expr):
                offset, arg = self.read_expression(expr[1:], rpos, absolute_pos=(absolute_pos if absolute_pos is not None else pos) + 5 + rpos, level=level + 1)
                rpos += offset 
                arguments.append(arg)
                
            return 4 + length, Operation(self, operator, *arguments, scope=scope, function=function)
        
        else:
            return 4 + length, self.read_literal(expr[1:], 0, scope, absolute_pos=(absolute_pos if absolute_pos is not None else pos) + 5, superlen=length)
        
    def read_instruction(self, data, pos, scope=None, absolute_pos=None, function=None):
        if absolute_pos is None:
            absolute_pos = pos
    
        length = struct.unpack("=L", data[pos: pos + 4])[0]
        instruction = data[pos + 4: pos + 4 + length]
        opcode = BASE_OPCODES[instruction[0]]
        
        instruction = instruction[1:]
        
        # print(opcode, hex(absolute_pos), data[pos:pos + 4 + length])
        
        # print(length, opcode)
        
        # print(" +", opcode, length, "@", hex(absolute_pos))
        
        arguments = []
        
        # print(hex(pos + 4), opcode, length)
        
        rpos = 0
        
        # print(opcode, "of length", length)
        
        while rpos + 1 < length:
            offset, arg = self.read_expression(instruction[rpos:], 0, scope, absolute_pos=absolute_pos + 5 + rpos, function=function)
            rpos += offset
            arguments.append(arg)
            
        # print(" @ ", opcode, len(arguments), ':', tuple(map(dbgvalue, arguments)))
            
        # print(absolute_pos, length, opcode, len(arguments))
            
        return length + 4, Instruction(self, scope, opcode, *arguments, function=function)
        
    def read(self, data, name=None):
        vlen = struct.unpack("=H", data[:2])[0]
        data = data[2:]
        v = data[:vlen].decode('utf-8')
        data = data[vlen:]
    
        if v != type(self).VERSION:
            raise VersionCheckError("The Netbyte code '{}' given to the interpreter is in the wrong version: '{}' instead of '{}'!".format(name, v, type(self).VERSION))
    
        pos = 0
        instructions = []
        
        while pos < len(data):
            offset, instruction = self.read_instruction(data, pos, absolute_pos=pos)
            pos += offset
            instructions.append(instruction)
            
        return instructions
        
    def execute(self, data, name=None):
        instructions = self.read(data, name)
        
        res = None
        pos = 0
        labels = {}
        
        while pos < len(instructions):
            i = instructions[pos]
            status = i.execute()
            
            if status is not None:
                if status == "SETRES":
                    res = self.last_return
                    self.last_return = None
                    
                elif status == "TERMINATE":
                    break
                    
                elif status[:5] == "JUMP:":
                    pos = int(status[5:])
                    
                elif status[:6] == "LJUMP:":
                    pos = labels[status[6:]]
                    
                elif status[:6] == "LABEL:":
                    labels[status.split(':')[1]] = pos + 1
                    pos = int(status.split(':')[2])
                
            if status is None or (status[:5] != "JUMP:" and status[:6] != "LJUMP:"):
                pos += 1
                
        return res

    def dump_expression(self, exp, debug=False, level=0):    
        res = b''
    
        if debug:
            print(" . " * level + " >", type(exp).__name__, repr(dbgvalue(exp)))
    
        if type(exp) is Instruction:
            r = self.dump(exp, debug=debug, level=level + 1)
            res = struct.pack("=LBLB", len(r) + 6, 0, len(r) + 1, TYPES.index("RTINST")) + r
            
            if debug: 
                print(" . " * level, len(r) + 5, res.hex())
                
            return res
            
        elif type(exp) is Operation:
            ores = struct.pack("=B", EXPR_OPCODES.index(exp.operator) + 1)

            for o in exp.operands:                    
                r = self.dump_expression(o, debug=debug, level=level + 1)
                ores += r
                
            # ores = struct.pack("=L", len(ores)) + ores
            res += ores
            
        elif type(exp) is Literal:
            res = b'\x00'
        
            if type(exp.value) is str:
                r = struct.pack('=LB{}s'.format(len(exp.value) + 1), len(exp.value.encode('utf-8')), TYPES.index('STRING'), exp.value.encode('utf-8'))
                res += r
                
            elif type(exp.value) in (tuple, list):
                ares = b''
                
                for i in exp.value:
                    ares += self.dump_expression(i)
            
                res += struct.pack("=LB", len(ares) + 1, TYPES.index('VARRAY')) + ares
                
            elif type(exp.value) is bool:
                res += struct.pack("=LB?", 2, TYPES.index("BOOLTF"), exp.value)
                
            elif type(exp.value) is int:
                if exp.value > 2147483647:
                    f = 'q'
                
                elif exp.value > 32767:
                    f = 'i'
                
                elif exp.value > 127:
                    f = 'h'
                    
                else:
                    f = 'b'
            
                r = struct.pack('=' + f, exp.value)
                res += struct.pack('=L', len(r)) + struct.pack('=B', TYPES.index('ITNUMS')) + r
                    
            elif type(exp.value) is float:
                r = struct.pack('=d', exp.value)
                res += struct.pack('=L', len(r))
                res += struct.pack('=B', TYPES.index('DBLNUM'))
                res += r
                
            else:
                res = struct.pack('=LBLB', 6, 0, 1, TYPES.index('NULLVL'))
                
                if debug: 
                    print(" . " * level, res.hex())
                
                return res
        
        res = struct.pack("=L", len(res)) + res
        
        if debug: 
            print(" . " * level, res.hex())
                
        return res
        
    def dump(self, *instructions, debug=False, level=0):
        res = b''
    
        for i in instructions:
            if debug:
                print(" . " * level + (i.opcode))
                
            ires = struct.pack('=B', BASE_OPCODES.index(i.opcode))
            
            for a in i.arguments:
                ires += self.dump_expression(a, debug=debug, level=level + 1)
            
            res += struct.pack("=L", len(ires)) + ires
            
            # print(dbgvalue(i), ires)
            
        return res
        
    def compile(self, *instructions, debug=False):
        return struct.pack('=H{}s'.format(len(type(self).VERSION)), len(type(self).VERSION), type(self).VERSION.encode('utf-8')) \
            + self.dump(*instructions, debug=debug)
        
    def execute_file(self, filename): 
        return self.execute(open(filename, 'rb').read(), filename)
        
    def parenthetic_parse(self, line):
        level = -1
        res = ""
        done = False
        
        for char in line:
            res += char
            
            if char in "])}":
                level -= 1
                # print(level, char, res)
                
            if level > -1:
                done = True    
            
            if char in "[({":
                level += 1
                # print(level, char, res)
                     
            if level < 0 and done:
                break          
            
        return res

    def argument_tree(self, line):
        res = []
        sub = ""
        parenthetic = False
        remaining = line
        quoted = False
        
        while len(remaining) > 0:
            char = remaining[0]
            
            if char == '"':
                quoted = not quoted
            
            if char in "[{(" and len(sub) == 0:
                p = self.parenthetic_parse(remaining)
                # print( ">", line, "   @   ", p)
                res.append(p)
                remaining = remaining[len(p):]
            
            else:
                remaining = remaining[1:]
            
                if char in ' ,' and not quoted:
                    res.append(sub)
                    sub = ""
                
                else:
                    sub += char
                
        if sub != "":
            res.append(sub)
            
        return res
        
    def parse_arg(self, argument):
        if type(argument) is str:
            if len(argument) > 1 and argument[0] == '"' and argument[-1] == '"':
                return Literal(self, argument[1:-1]
                    .replace(r'\n', '\n')
                    .replace(r'\"', '"')
                    .replace(r'\'', "'")
                    .replace('\\\\', '\\')
                )
            
            elif '(' in argument and argument[0] != '(' and argument[-1] == ')':
                scope = ''
                name = ''
                
                while True:
                    if argument[0] == '(':
                        break
                        
                    name += argument[0]
                    
                    if name.endswith('::'):
                        scope = name[:-2]
                        name = ''
                        
                    argument = argument[1:]
                
                args = tuple(map(self.parse_arg, filter(lambda x: len(x) > 0, self.argument_tree(self.parenthetic_parse(argument[1:-1].strip(' '))))))
                    
                return Operation(self, "FNCALL", Literal(self, name), Literal(self, scope), *args)
            
            elif argument[0] == "{" and argument[-1] == "}":
                argument = argument[1:-1].strip(' ')
                args = list(map(self.parse_arg, filter(lambda x: len(x) > 0, self.argument_tree(' '.join(argument.split(' ')[1:])))))
            
                return Instruction(
                    self, None,
                    argument.split(' ')[0],
                    *args
                )
                
            elif argument[0] == "(" and argument[-1] == ")":
                argument = argument[1:-1].strip(' ')
                
                code = argument.split(' ')[0]    
                args = tuple(map(self.parse_arg, filter(lambda x: len(x) > 0, self.argument_tree(' '.join(argument.split(' ')[1:])))))
            
                return Operation(self, code, *args)
                
            elif argument[0] == "[" and argument[-1] == "]":
                argument = argument[1:-1].strip(' ')
                
                res = []
                sub = ""
                is_str = False
                
                for c in argument:
                    if c == ":" and not is_str:
                        res.append(self.parse_arg(sub))
                        sub = ""
                
                    else:
                        sub += c
                        
                        if c == '"':
                            is_str = not is_str
                        
                return Literal(self, res)
                
            elif argument.upper() in ("NULL", "NONE"):
                return Literal(self, None)
                
            elif argument.upper() == "TRUE":
                return Literal(self, True)
                
            elif argument.upper() == "FALSE":
                return Literal(self, False)
                
            elif len(tuple(filter(lambda x: x in '0123456789', argument))) == len(argument):
                return Literal(self, int(argument))
                
            elif argument.count('.') == 1 \
                    and len(filter(lambda x: x in '0123456789', argument.split('.')[0])) == len(argument.split('.')[0])\
                    and len(filter(lambda x: x in '0123456789', argument.split('.')[1])) == len(argument.split('.')[1]):
                return Literal(self, float(argument))
                
            elif argument.startswith('0x') and len(filter(lambda x: x in '0123456789ABCDEF', argument[2:])) == len(argument) - 2:
                return Literal(self, int(argument[2:], 16))
                
            elif argument.startswith('0o') and len(filter(lambda x: x in '01234567', argument[2:])) == len(argument) - 2:
                return Literal(self, int(argument[2:], 8))
                
            elif argument.startswith('0b') and len(filter(lambda x: x in '01', argument[2:])) == len(argument) - 2:
                return Literal(self, int(argument[2:], 2))
                
            else:
                return Operation(self, "GETVAR", Literal(self, argument), Literal(self, None))
                    
        return Literal(self, None)
                    
    def parse(self, assembly, name=None):
        instructions = []
        assembly = re.sub(r'//[^\n]+', '', assembly)
        assembly = re.sub(r' +', ' ', assembly)
    
        for l in re.split(r'(?<!\\)\n', assembly):
            l = l.replace('\\\n', ' ')
            l = l.strip(' ')
        
            if re.sub(r'^\s+$', '', l) == '':
                continue
        
            opcode = l.split(' ')[0]
            
            if opcode not in BASE_OPCODES:
                warnings.warn("Code @ '{}': {} is not a valid opcode!".format(name, opcode))
            
            arguments = tuple(map(self.parse_arg, filter(lambda x: len(x) > 0, self.argument_tree(' '.join(l.split(' ')[1:])))))
            # print(arguments)
            instructions.append(Instruction(self, None, opcode, *arguments))
        
        return instructions
        
    def parse_file(self, filename):
        return self.parse(open(filename).read(), filename)