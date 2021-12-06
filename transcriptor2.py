import AST
from AST import addToClass
from functools import reduce
import math
import numpy as np
from PIL import Image
from ast import literal_eval as string_to_tuple
from math import log

# 8 would mean 256 instructions
MAX_INSTRUCTIONS_BIT_SIZE = 8 # hide each on 8 bits

# 3 would mean 8 differents var
MAX_VAR_BIT_SIZE = 8

# 5 would mean numeric values goes from -16 to 15
MAX_NUM_BIT_SIZE = 8

transcriptor_dict = {
    'EMPTY': 0,
    'PUSHV': 1,
    'PUSHC': 2,
    'SET'  : 3,
    'ADD'  : 4,
    'SUB'  : 5,
    'MUL'  : 6,
    'DIV'  : 7,
    'PRINT': 8,
    'USUB' : 9,
    'JMP'  : 10,
    'JIZ'  : 11,
    'JINZ' : 12,
    'var' : lambda x: (13, x),
    'num' : lambda x: (14, x),
    'body' : lambda x: (15, x),
    'cond' : lambda x: (16, x),
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

NEGATIVE = 0
POSITIVE = 1
def num_to_rgb(num):
    if num > pow(2, MAX_NUM_BIT_SIZE)-1 or num < -pow(2, MAX_NUM_BIT_SIZE):
        raise Exception('number too big or too short')
    x = int(num)
    return transcriptor_dict['num'](x)

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

def get_instruction(instruction):
    try:
        return int(instruction) # is it an int
    except ValueError: # this is a tuple
        return string_to_tuple(instruction)

def split_into_bits(value, max_bits):
    if (value == 0):
        return [0 for _ in range(max_bits)]
    value_nb_bits = int(log(value, 2)+1)
    if value_nb_bits > max_bits:
        raise Exception(f'value too big for max_bits, value is {value} ({value_nb_bits} bits are needed), but max allowed bits are {max_bits}')

    ret = []

    for i in range(max_bits):
        i = max_bits - i -1
        powed = pow(2, i)
        if value / powed >= 1:
            ret.append(1)
            value -= powed
        else:
            ret.append(0)

    return ret

def increment(row, column, array):
    column += 1
    if column >= array.shape[0]:
        column = 0
        row += 1
    return row, column

def controle_size(size, image):
    pass
    # TODO
    # + expand_on_pixels => add EOF after the code is written
    # if (size*size + step_expand_on_pixels > image.shape[0] * image.shape[1]):
    #     print('invalid picture size')
    #     exit(-1)

def change_bit(bit, image, row_counter, column_counter, rgb_counter):
    '''rgb_value is {2, 1, 0} in rgb (...[2] means red value of pixel)'''

    actual_color = image[row_counter][column_counter][rgb_counter]
    
    if actual_color % 2 == 0 and bit == 1:
        image[row_counter][column_counter][rgb_counter] += 1
    elif actual_color % 2 == 1 and bit == 0:
        image[row_counter][column_counter][rgb_counter] -= 1
        
    rgb_counter += 1
    if rgb_counter == 3:
        rgb_counter = 0
        row_counter, column_counter = increment(row_counter, column_counter, image)
    
    return row_counter, column_counter, rgb_counter

def generate_image(s, source_image_path, output_image_path):
    print(f'source is {source_image_path}')
    print(f'output is {output_image_path}')
    
    instructions = s.split('\n')[:-1] # remove last line (always empty line)
    import cv2
    image = cv2.imread(source_image_path, cv2.IMREAD_COLOR)
    
    # TODO
    # size = int(math.sqrt(transcript.pixels_counter * step_expand_on_pixels)) + 1
    # controle_size(size, image)

    column_counter = 0
    row_counter = 0
    rgb_counter = 0

    for instruction in instructions: # instruction is str
        instruction = get_instruction(instruction)
        value = None
        if (type(instruction) is tuple):
            value = instruction[1]
            instruction = instruction[0]

        for bit in split_into_bits(instruction, MAX_INSTRUCTIONS_BIT_SIZE):
            row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)

        was_a_num = instruction == transcriptor_dict['num'](0)[0]
        # add var id or num value
        if (value is not None):
            x = MAX_NUM_BIT_SIZE if was_a_num else MAX_VAR_BIT_SIZE
            for bit in split_into_bits(value, x):
                row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
            
    # apply "EOF"
    for bit in split_into_bits(transcriptor_dict['EMPTY'], MAX_NUM_BIT_SIZE):
        row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
    
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.imwrite(output_image_path, image)


def bit_array_to_int(arr):
    arr.reverse()
    x = 0
    for i in range(len(arr)):
        x += arr[i] * pow(2, i)

    return x    

was_last_operation_linked_with_body_or_cond = False
was_last_operation_a_var = False
was_last_operation_a_num = False
was_last_operation_a_body = False
was_last_operation_a_cond = False
shall_get_number = True


def decode(code_rgb):
    '''headhache assured on this function'''
    
    global was_last_operation_linked_with_body_or_cond
    global was_last_operation_a_var
    global was_last_operation_a_num
    global was_last_operation_a_body
    global was_last_operation_a_cond

    # false when you have to add : and no \n to the line
    # true for the inverse
    # ex.
    # body0: PUSHC 3\n    # false
    # JINZ body0\n        # true
    old_was_last_operation_linked_with_body_or_cond = was_last_operation_linked_with_body_or_cond
    if code_rgb != transcriptor_dict['body'](0)[0] and code_rgb != transcriptor_dict['cond'](0)[0]:
        was_last_operation_linked_with_body_or_cond = (
            code_rgb == transcriptor_dict['JMP']
            or code_rgb == transcriptor_dict['JINZ'])

    print(f'{old_was_last_operation_linked_with_body_or_cond} when {inv_transcriptor_dict[code_rgb] if can_invert(code_rgb) else code_rgb}')

    if code_rgb == transcriptor_dict['var'](0)[0]:
        was_last_operation_a_var = True
        return ' ', False

    elif was_last_operation_a_var:
        was_last_operation_a_var = False
        return f'var{code_rgb}', True
    
    elif code_rgb == transcriptor_dict['num'](0)[0]:
        was_last_operation_a_num = True
        return ' ', False

    elif was_last_operation_a_num:
        was_last_operation_a_num = False
        return f'{code_rgb}', True
    
    elif code_rgb == transcriptor_dict['body'](0)[0]:
        was_last_operation_a_body = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False
    
    elif was_last_operation_a_body:
        was_last_operation_a_body = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'body{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond

    elif code_rgb == transcriptor_dict['cond'](0)[0]:
        was_last_operation_a_cond = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False
    
    elif was_last_operation_a_cond:
        was_last_operation_a_cond = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'cond{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond


    was_last_operation_a_var = code_rgb == transcriptor_dict['var']
    was_last_operation_a_num = code_rgb == transcriptor_dict['num']

    # TODO refactor
    should_new_line = not (
        code_rgb == transcriptor_dict['PUSHC']
        or code_rgb == transcriptor_dict['PUSHV']
        or code_rgb == transcriptor_dict['SET']
        or code_rgb == transcriptor_dict['JMP']
        or code_rgb == transcriptor_dict['JINZ'])
    
    return inv_transcriptor_dict[code_rgb], should_new_line

def run_image(image_array):
    from svm import run
    code = ''

    row_counter = 0
    column_counter = 0
    rgb_counter = 0

    for _ in range(image_array.shape[0] * image_array.shape[1]):
        x = []
        for _ in range(MAX_INSTRUCTIONS_BIT_SIZE):
            x.append(image_array[row_counter][column_counter][rgb_counter])
            rgb_counter += 1
            if rgb_counter == 3:
                rgb_counter = 0
                row_counter, column_counter = increment(row_counter, column_counter, image_array)
        
        code_as_bit = bit_array_to_int(x)
        if (code_as_bit == transcriptor_dict['EMPTY']
        and not was_last_operation_a_num
        and not was_last_operation_a_var
        and not was_last_operation_a_cond
        and not was_last_operation_a_body):
            break

        decoded, should_new_line = decode(code_as_bit)
        
        new_line = '\n' if should_new_line else ''
        code += f'{decoded}{new_line}'

    # TODO: change behavior, instead of writing to file, give string
    opcode_filename = 'output.vm'
    with open(opcode_filename, 'w') as f:
        f.write(code)
    
    print(code)

    run(opcode_filename)

    import os
    try:
        pass
        os.remove(opcode_filename)
    except:
        print('unknown error')    

def print_help_and_exit():
    s = f"""
    HOW TO USE

    first arg must be [{arg_generate} | {arg_run}]
    second arg must be the path to the code file
    third arg must be the path to the source image when generating

    ex.
    python transcriptor.py {arg_generate} my_code.txt image_source.png
    python transcriptor.py {arg_run} my_code_picture.bmp
    ____________________________________________________"""
    print(s)
    exit(0)

def get_args():
    return sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print_help_and_exit()

    mode, file_path, source_image_path = get_args()

    if mode == arg_generate:
        if (source_image_path is None):
            print_help_and_exit()

        from parser5 import parse
        import re
        
        print('generating picture from code...\n')

        x = re.search("^(.+)\..+$", source_image_path)
        IMAGE_EXTENSION = 'bmp'
        output = f'code_{x.group(1)}.{IMAGE_EXTENSION}'

        with open(file_path) as f:
            prog = f.read()
        
        ast = parse(prog)

        transcriptd = ast.transcript()
        generate_image(transcriptd, source_image_path, output)       
        
    elif mode == arg_run:
        import cv2
        print('running picture...\n')
        
        image = cv2.imread(file_path)
        run_image(image)

    else:
        print_help_and_exit()
