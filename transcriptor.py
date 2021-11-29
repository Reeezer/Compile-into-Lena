import AST
from AST import addToClass
from functools import reduce
import math
import numpy as np
from PIL import Image
from ast import literal_eval as string_to_tuple

transcriptor_dict = {
    'EMPTY': (0, 0, 0),
    'PUSHV': (0, 255, 0),
    'PUSHC': (0, 254, 0),
    'SET'  : (255, 0, 255),
    'ADD'  : (255, 254, 33),
    'SUB'  : (203, 61, 1),
    'MUL'  : (155, 142, 16),
    'DIV'  : (255, 28, 119),
    'PRINT': (255, 143, 119),
    'USUB' : (121, 97, 243),
    'JMP'  : (206, 63, 215),
    'JIZ'  : (3, 248, 185),
    'JINZ' : (42, 143, 119),
    'var' : lambda x: (0, x, 255),
    'num' : lambda x, y: (122, x, y),
    'body' : lambda x: (80, 140, x),
    'cond' : lambda x: (200, 0, x),
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
    x = transcriptor_dict['var'](transcript.var_counter)
    vars[var] = x
    transcript.var_counter += 1
    return x

def num_to_rgb(num):
    if num > 255 or num < -255:
        raise Exception
    x = 1 if num >= 0 else 0
    return transcriptor_dict['num'](x, int(num))

def body_to_rgb(counter):
    return transcriptor_dict['body'](counter)

def cond_to_rgb(counter):
    return transcriptor_dict['cond'](counter)

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
    ret += f"{body}\n"
    ret += self.children[1].transcript()

    ret += f"{cond}\n"
    ret += self.children[0].transcript()
    ret += f"{jinz}\n{body}\n"

    transcript.pixels_counter += 6

    return ret

transcript.while_flag = 0
transcript.var_counter = 0
transcript.pixels_counter = 0

def generate_image(s, output):
    size = int(math.sqrt(transcript.pixels_counter)) + 1
    print(f'SIZE IS {size}')
    
    colors = s.split('\n')[:-1] # remove last line (always empty line)
    counter = 0
    image_array = np.empty((size, size, 3), dtype=np.uint8)

    for i in range(size):
        for j in range(size):
            if counter >= len(colors):
                image_array[i, j] = transcriptor_dict['EMPTY']
            else:
                image_array[i, j] = string_to_tuple(colors[counter])
            counter += 1
    
    image = Image.fromarray(image_array)
    image.show()
    image.save(output)

if __name__ == '__main__':
    from parser5 import parse
    import sys, os
    import re
    
    input = sys.argv[1]
    
    x = re.search("^(.+)\..+$", input)
    IMAGE_EXTENSION = 'bmp'
    output = f'{x.group(1)}.{IMAGE_EXTENSION}'

    prog = open(input).read()
    ast = parse(prog)

    transcriptd = ast.transcript()

    generate_image(transcriptd, output)

    print(transcript.pixels_counter)
    