import AST
from AST import addToClass
from functools import reduce
import math

transcriptor_dict = {
    'RIP' : (0, 0, 0),
    'PUSHV': (0, 255, 0),
    'PUSHC': (0, 254, 0),
    'SET'  : (255, 0, 255),
    'ADD'  : (1, 0, 0),
    'SUB'  : (1, 0, 1),
    'MUL'  : (1, 0, 2),
    'DIV'  : (1, 0, 3),
    'PRINT': (0, 0, 1),
    'USUB' : (0, 0, 2),
    'JMP'  : (0, 0, 3),
    'JIZ'  : (0, 0, 4),
    'JINZ' : (0, 0, 5)
}

operations = {
    '+': lambda x,y: f"{x}{y}{transcriptor_dict['ADD']}\n",
    '-': lambda x,y: f"{x}{y}{transcriptor_dict['SUB']}\n",
    '*': lambda x,y: f"{x}{y}{transcriptor_dict['MUL']}\n",
    '/': lambda x,y: f"{x}{y}{transcriptor_dict['DIV']}\n",
}

vars = {}

def var_to_rgb(var):
    if var in vars.keys():
        return vars[var]
    
    x = (50, 0, transcript.var_counter)
    vars[var] = x
    transcript.var_counter += 1
    return x

def num_to_rgb(num):
    if num > 255 or num < -255:
        raise Exception
    x = 1 if num >= 0 else 0
    return (40, x, int(num))

def body_to_rgb(counter):
    return (10, 0, counter)

def cond_to_rgb(counter):
    return (11, 0, counter)

@addToClass(AST.ProgramNode)
def transcript(self):
    ret = ''
    for c in self.children:
        ret += c.transcript()
    return ret

@addToClass(AST.TokenNode)
def transcript(self):
    if isinstance(self.tok, str):
        x = transcriptor_dict['PUSHV']
        v = var_to_rgb(self.tok)
    else:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(self.tok)

    transcript.pixels_counter += 2
    return f"{x}\n{v}\n"

@addToClass(AST.OpNode)
def transcript(self):
    args = [c.transcript() for c in self.children]
    if len(args) == 1:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(0)

        transcript.pixels_counter += 2
        args.insert(0, f"{x}\n{v}\n")

    transcript.pixels_counter += 1
    return reduce(operations[self.op], args)

@addToClass(AST.AssignNode)
def transcript(self):
    ret = self.children[1].transcript()

    x = transcriptor_dict['SET']
    v = var_to_rgb(self.children[0].tok)

    transcript.pixels_counter += 2

    ret += f"{x}\n{v}\n"
    
    return ret

@addToClass(AST.PrintNode)
def transcript(self):
    ret = self.children[0].transcript()

    x = transcriptor_dict['PRINT']
    
    transcript.pixels_counter += 1

    ret += f"{x}\n"

    return ret

@addToClass(AST.WhileNode)
def transcript(self):
    counter = transcript.while_flag
    transcript.while_flag += 1

    jmp = transcriptor_dict['JMP']
    cond = cond_to_rgb(counter)
    body = body_to_rgb(counter)
    jinz = transcriptor_dict['JINZ']
    
    ret = f"{jmp}\n{cond}\n"
    ret += f"{body}"
    ret += self.children[1].transcript()

    ret += f"{cond}"
    ret += self.children[0].transcript()
    ret += f"{jinz}\n{body}\n"

    transcript.pixels_counter += 6

    return ret

transcript.while_flag = 0
transcript.var_counter = 0
transcript.pixels_counter = 0

def picture_thingy(s): #TODO modifier els noms de variables
    size = int(math.sqrt(transcript.pixels_counter)) + 1
    print(f'SIZE IS {size}')
    arr = s.split('\n')[:-1]
    arr_counter = 0
    ss = ''
    for i in range(size):
        for j in range(size):
            if arr_counter >= len(arr):
                ss += f"{transcriptor_dict['PUSHC']} "
            else:
                ss += f'{arr[arr_counter]} '
            arr_counter += 1
        print(ss[:-1])
        ss = ''

if __name__ == '__main__':
    from parser5 import parse
    import sys, os

    prog = open(sys.argv[1]).read()
    ast = parse(prog)

    transcriptd = ast.transcript()

    picture_thingy(transcriptd)

    print(transcript.pixels_counter)
    