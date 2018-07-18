import struct
import time
import math
import importlib

from socket import socket, AF_INET, SOCK_STREAM, error as SocketError

# Note that optional arguments default to None (Python) or NULLVL (Netbyte).

# Base Operations
BASE_OPCODES = [
    "SETVAR", # Set Variable : string name, string scope, any value
    "DELVAR", # Delete Variable : string name
    "MKFUNC", # Make Function : string name, byte string expressions, optional string scope
    "RETURN", # Set return value
    "TERMIN", # Terminate
    "JUMPTO", # Jump To instruction at position...
    "JUMPLB", # Jump to Label
    "MLABEL", # Mark Label
    "EXFILE", # Execute File
    "PRINTV", # Print Value
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
]

# Expression Operators
EXPR_OPCODES = [
    # Generic Operators
    "GETVAR", # Retrieve Variable : string name, string scope -> any

    # Comparison Operators
    "EQUALS", # Equation : 2+ any -> bool
    "DIFFER", # Differentiation : 2+ any -> bool
    
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
    
    # Misc Operators
    "FNCALL", # Function Call : string (name), optional string (scope), 0+ anything -> anything
    "NFCALL", # Native Function Call : string (name), string (module), 0+ anything (no kwargs) -> anything
]

def exvalue(expr, *args, **kwargs):
    return expr.__value__(*args, **kwargs)
        
class Expression(object):
    def __value__(self):
        raise RuntimeError("Expression objects can't be used directly!")
        
class Operation(Expression):
    def __init__(self, environment, operator, *args, scope=None):
        self.operator = operator
        self.operands = args
        self.scope = scope
        
    def __value__(self):
        operands = map(exvalue, self.operands)
    
        if self.operator == "GETVAR":
            return self.environment.variables[operands[1]][operands[0]]
    
        if self.operator == "EQUALS":
            return len(set(operands)) < 2
            
        if self.operator == "DIFFER":
            return len(set(operands)) > 1
    
        if self.operator == "ADDNUM":
            return sum(operands)
            
        if self.operator == "SUBNUM":
            return operands[0] - operands[1]
            
        if self.operator == "MULNUM":
            return reduce(lambda a, b: a * b, operands, 0)
            
        if self.operator == "DIVNUM":
            return operands[0] / operands[1]
            
        if self.operator == "POWNUM":
            return math.pow(operands[0], operands[1])
            
        if self.operator == "ROTNUM":
            return math.pow(operands[0], 1.0 / operands[1])
            
        if self.operator == "ANDNUM":
            return reduce(lambda a, b: a & b, operands, 0)
            
        if self.operator == "IORNUM":
            return reduce(lambda a, b: a | b, operands, 0)
            
        if self.operator == "XORNUM":
            return reduce(lambda a, b: a ^ b, operands, 0)
            
        if self.operator == "NOTNUM":
            return ~operands[0]
            
        if self.operator == "SSLICE":
            return operands[0][operands[1]: operands[2]]
            
        if self.operator == "CONCAT":
            return sum(operands)
            
        if self.operator == "SPSCHR":
            return operands[0][operands[1]]
            
        if self.operator == "FNCALL":
            return self.environment.functions[operands[1]][operands[0]].execute(operands[2:])
            
        if self.operator == "NFCALL":
            return getattr(importlib.import_module(operands[1]), operands[0])(operands[2:])
        
class Literal(Expression):
    def __init__(self, environment, value):
        self.environment = environment
        self.value = value

    def __value__(self):
        return self.value
        
class FunctionCall(Expression):
    def __init__(self, environment, name, *args, scope=None):
        self.environment = environment
        self.scope = scope
        self.name = name
        self.args = args
        
    def __value__(self):
        return self.environment.functions[self.scope][self.name].execute(self.args)

class Function(object):
    def __init__(self, environment, scope, name, *instructions):
        self.environment = environment
        self.scope = scope
        self.name = name
        self.instructions = instructions
        
    def __hash__(self):
        return hash(self.scope.replace(':', '_') + "::" + self.name.replace(':', '_'))
        
    def execute(self):
        res = None
        labels = {}
        pos = 0
        
        while pos < len(self.instructions):
            i = self.instructions[pos]
            status = i.execute()
            
            if status is None or (status[:5] != "JUMP:" and status[:6] != "LJUMP:"):
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
        
    def execute(self):
        arguments = list(map(exvalue, self.arguments))
    
        if self.opcode == 'SETVAR':
            sc = (arguments[1] if arguments[1] is not None else self.scope)
        
            if sc not in self.environment.variables:
                self.environment.variables[sc] = {}
        
            self.environment.variables[sc][arguments[0]] = arguments[2]
            
        elif self.opcode == 'DELVAR':
            if self.scope in self.environment.variables and arguments[0] in self.environment.variables[self.scope]:
                self.environment.variables[self.scope].pop(arguments[0])
                
        elif self.opcode == 'MKFUNC':
            name = arguments[0]
            scope = arguments[1]
            instructions = arguments[2:]
            
            if scope is not None:
                for i in instructions:
                    i.scope = scope
            
            sc = (scope if scope is not None else self.scope)
            
            self.environment.functions[sc][name] = Function(self.environment, sc, name, *instructions)
            
        elif self.opcode == "RETURN":
            if self.function:
                self.environment.return_stack[self.function] = arguments[0]
                
            else:
                self.environment.last_return = arguments[0]
                
            return "SETRES"
            
        elif self.opcode == "TERMIN":
            return "TERMINATE"
            
        elif self.opcode == "JUMPTO":
            return "JUMP:" + str(arguments[0])
            
        elif self.opcode == "MLABEL":
            return "LABEL:{}:{}".format(arguments[0], arguments[1])
            
        elif self.opcode == "JUMPLB":
            return "LJUMP:" + arguments[0]
            
        elif self.opcode == "EXFILE":
            self.environment.execute(open(self.arguments[0], 'rb').read())
                        
        elif self.opcode == "PRINTV":
            print(*arguments)
            
    def __value__(self):
        self.execute()
        
class Interpreter(object):
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.return_stack = {}
        self.files = []
        self.last_return = None
        
    def _get_str(self, data, pos):
        length = struct.unpack("=I", data[pos: pos + 4])[0]
        sd = data[pos + 4: pos + 4 + length]
        return sd.decode('utf-8')
        
    def read_literal(self, data, pos, scope=None):
        ltype = TYPES[data[pos]]
        length = struct.unpack("=L", data[pos + 1 : pos + 5])[0]
        sd = data[pos + 5:pos + 5 + length]
        
        if ltype == "NULLVL":
            return Literal(self, None)
            
        elif ltype == "ITNUMS":
            res = 0
            
            for i, char in enumerate(sd):
                res += struct.unpack("=B", char)[0] * math.pow(2, i)
                
            return Literal(self, int(res) - int(math.pow(2, len(sd) - 1)) - 1)
            
        elif ltype == "ITNUMU":
            res = 0
            
            for i, char in enumerate(sd):
                res += char * math.pow(2, i)
                
            return Literal(self, int(res))
            
        elif ltype == "FLTNUM":
            return Literal(self, struct.unpack("=f", sd[:4])[0])
            
        elif ltype == "DBLNUM":
            return Literal(self, struct.unpack("=d", sd[:8])[0])
            
        elif ltype == "STRING":
            return Literal(self, sd.decode('utf-8'))
            
        elif ltype == "RTINST":
            return self.read_instruction(sd, 0, scope)
        
    def read_expression(self, data, pos, scope=None, absolute_pos=None, level=0):
        length = struct.unpack("=L", data[pos: pos + 4])[0]
        # print(hex(absolute_pos if absolute_pos is not None else pos), length, "L" + str(level))
        expr = data[pos + 4: pos + 4 + length]
        
        if expr[0] > 0:
            operator = EXPR_OPCODES[expr[0] - 1]
            # print(">", hex((absolute_pos if absolute_pos is not None else pos) + 3), expr[0], operator)
            rpos = 0
            arguments = []
            
            while rpos + 1 < len(expr):
                offset, arg = self.read_expression(expr[1:], rpos, absolute_pos=(absolute_pos if absolute_pos is not None else pos) + 5 + rpos, level=level + 1)
                rpos += offset 
                arguments.append(arg)
                
            return 4 + length, Operation(self, operator, *arguments, scope=scope)
        
        else:
            return 4 + length, self.read_literal(expr, 1, scope)
        
    def read_instruction(self, data, pos, scope=None):
        length = struct.unpack("=L", data[pos: pos + 4])[0]
        instruction = data[pos + 4: pos + 4 + length]
        
        opcode = BASE_OPCODES[instruction[0]]
        arguments = []
        
        # print(hex(pos + 4), opcode, length)
        
        rpos = 1
        
        while rpos < len(instruction):
            offset, arg = self.read_expression(instruction, rpos, scope, absolute_pos=pos + 5 + rpos)
            rpos += offset
            arguments.append(arg)
            
        return length + 4, Instruction(self, scope, opcode, *arguments)
        
    def read(self, data):
        pos = 0
        instructions = []
        
        while pos < len(data):
            offset, instruction = self.read_instruction(data, pos)
            pos += offset
            instructions.append(instruction)
            
        return instructions
        
    def execute(self, data):
        instructions = self.read(data)
        
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
        
    def execute_file(self, filename): 
        return self.execute(open(filename, 'rb').read())