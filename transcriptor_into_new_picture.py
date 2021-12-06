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

def can_invert(key):
    try:
        tuple(key)
        return True
    except Exception:
        return False

# reverse the dict
inv_transcriptor_dict = {v: k for k, v in transcriptor_dict.items() if can_invert(k)}

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
    neg = 1 if num >= 0 else 0
    return transcriptor_dict['num'](neg, int(num))

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

arg_generate = '-g'
arg_run = '-r'

step_expand_on_pixels = 3

def increment(row, column, array):
    column += 1
    if column >= array.shape[0]:
        column = 0
        row += 1
    return row, column

def generate_image(s, output):
    size = int(math.sqrt(transcript.pixels_counter * step_expand_on_pixels)) + 1
    
    colors = s.split('\n')[:-1] # remove last line (always empty line)
    counter = 0
    
    import cv2
    image = cv2.imread("blank.png", cv2.IMREAD_COLOR)
    
    # + expand_on_pixels => add EOF after the code is written
    if (size*size + step_expand_on_pixels > image.shape[0] * image.shape[1]):
        print('invalid picture size')
        exit(-1)

    should_break = False
    # use only the red value of picture => after that change to use only last two pixels of picture
    column_counter = 0
    row_counter = 0
    for pix in colors:
        pix = string_to_tuple(pix)
        for c in pix:
            image[row_counter][column_counter][0] = c
            row_counter, column_counter = increment(row_counter, column_counter, image)

    # apply "EOF"
    for c in transcriptor_dict['EMPTY']:
            image[row_counter][column_counter] = c
            row_counter, column_counter = increment(row_counter, column_counter, image)
    
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.imwrite(output, image)

was_last_operation_linked_with_body_or_cond = False

def decode(code_rgb):
    global was_last_operation_linked_with_body_or_cond
    r, g, b = code_rgb

    rgb = (r, g, b)
    local_was_thing = was_last_operation_linked_with_body_or_cond
    was_last_operation_linked_with_body_or_cond = rgb == transcriptor_dict['JMP'] or rgb == transcriptor_dict['JINZ']

    # verify if a lambda was used
    if r == transcriptor_dict['var'](0)[0] and b == transcriptor_dict['var'](0)[2]:
        return f'var{g}', True
    
    elif r == transcriptor_dict['num'](0, 0)[0]:
        neg = '-' if g == 0 else ''
        return f'{neg}{b}', True
    
    elif r == transcriptor_dict['body'](0)[0] and g == transcriptor_dict['body'](0)[1]:
        double_dot = ':' if not local_was_thing else ''
        return f'body{b}{double_dot}', local_was_thing

    elif r == transcriptor_dict['cond'](0)[0] and g == transcriptor_dict['cond'](0)[1]:
        double_dot = ':' if not local_was_thing else ''
        return f'cond{b}{double_dot}', local_was_thing


    # TODO refactor
    should_new_line = not (
        rgb == transcriptor_dict['PUSHC']
        or rgb == transcriptor_dict['PUSHV']
        or rgb == transcriptor_dict['SET']
        or rgb == transcriptor_dict['JMP']
        or rgb == transcriptor_dict['JINZ'])
    
    return inv_transcriptor_dict[rgb], should_new_line

def run_image(image_array):
    from svm import run
    code = ''

    row_counter = 0
    column_counter = 0

    for _ in range(0, image_array.shape[0] * image_array.shape[1], step_expand_on_pixels):
        x = []
        for _ in range(3):
            x.append(image_array[row_counter][column_counter][0])
            print(x)
            row_counter, column_counter = increment(row_counter, column_counter, image_array)
        
        cell = tuple(x)
        if cell == transcriptor_dict['EMPTY']:
            break

        decoded, should_new_line = decode(cell)
        
        new_line = '\n' if should_new_line else ' '
        code += f'{decoded}{new_line}'

    print(code)
    # TODO: change behavior, instead of writing to file, give string
    opcode_filename = 'output.vm'
    with open(opcode_filename, 'w') as f:
        f.write(code)
    
    run(opcode_filename)

    import os
    try:
        pass
        os.remove(opcode_filename)
    except:
        print('unknown error')    

def print_help():
    s = f"""
    HOW TO USE

    first arg must be [{arg_generate} | {arg_run}]
    second arg must be the path to the file

    ex.
    python transcriptor.py {arg_generate} my_code.txt
    python transcriptor.py {arg_run} my_code_picture.bmp
    ____________________________________________________"""
    print(s)

def get_args():
    return sys.argv[1], sys.argv[2] 

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print_help()
        exit(0)

    mode, file_path = get_args()
    if mode == arg_generate:
        from parser5 import parse
        import re
        
        print('generating picture from code...\n')
        x = re.search("^(.+)\..+$", file_path)
        IMAGE_EXTENSION = 'bmp'
        output = f'{x.group(1)}.{IMAGE_EXTENSION}'

        with open(file_path) as f:
            prog = f.read()
        
        ast = parse(prog)

        transcriptd = ast.transcript()
        generate_image(transcriptd, output)       
        
    elif mode == arg_run:
        import cv2

        print('running picture...\n')
        
        image = cv2.imread(file_path)
        run_image(image)

    else:
        print_help()