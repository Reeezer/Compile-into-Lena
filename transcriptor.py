import AST
from AST import addToClass
from functools import reduce
from ast import literal_eval as string_to_tuple
from math import log

# thoses MAX means "how much memory is allowed for each thing"
# meaning for a var of 26 each variable will use 26/3 pixels
# and also a maximum of 67108864 differents variables
# 8 would mean maximum 256 instructions
MAX_INSTRUCTIONS_BIT_SIZE = 8 # hide each on 8 bits
# 3 would mean 8 differents var
MAX_VAR_BIT_SIZE = 8
# 5 would mean numeric values goes from -16 to 15
MAX_NUM_BIT_SIZE = 9
# same but for conditions
MAX_CONDITIONS_BIT_SIZE = 8
# same but for bodys
MAX_BODIES_BIT_SIZE = 8

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
    'MOD' : 13,
    'POW' : 14,
    'PASS' : 15,
    'VAR' : lambda x: (13, x),  # the size is MAX_INSTRUCTIONS + MAX_VAR
    'NUM' : lambda x: (14, x),  # the size is MAX_INSTRUCTIONS + MAX_NUM
    'BODY' : lambda x: (15, x), # the size is MAX_INSTRUCTIONS + MAX_BODY
    'COND' : lambda x: (16, x), # the size is MAX_INSTRUCTIONS + MAX_COND
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
    '%': lambda x,y: f"{x}{y}{transcriptor_dict['MOD']}\n",
    '^': lambda x,y: f"{x}{y}{transcriptor_dict['POW']}\n",
}


def verify_limits(value, limit, error, is_unsigned):
    if is_unsigned:
        if value > pow(2, limit):
            raise Exception(error)
    else:
        if value > pow(2, limit-1) -1 or value < -pow(2, limit-1):
            raise Exception(error)

vars = {}
def var_to_rgb(var):
    if var in vars.keys():
        transcript.var_counter += 1
        transcript.instructions_counter += 1
        return vars[var]
    verify_limits(var_to_rgb.var_name_counter, MAX_VAR_BIT_SIZE, 'too much var', True)
    x = transcriptor_dict['VAR'](var_to_rgb.var_name_counter)
    var_to_rgb.var_name_counter += 1
    vars[var] = x
    transcript.var_counter += 1
    transcript.instructions_counter += 1
    return x

NEGATIVE = 0
POSITIVE = 1
def num_to_rgb(num):
    verify_limits(num, MAX_NUM_BIT_SIZE, 'number too big or too short', False)
    x = int(num)
    transcript.const_counter += 1
    transcript.instructions_counter += 1
    return transcriptor_dict['NUM'](x)

def body_to_rgb():
    verify_limits(body_to_rgb.body_name_counter, MAX_BODIES_BIT_SIZE, 'too much bodies', True)
    transcript.body_counter += 2 # each time, two are used
    transcript.instructions_counter += 2 # each time, two are used
    ret = transcriptor_dict['BODY'](body_to_rgb.body_name_counter)
    body_to_rgb.body_name_counter += 1
    return ret

def cond_to_rgb():
    verify_limits(cond_to_rgb.cond_name_counter, MAX_CONDITIONS_BIT_SIZE, 'too much conditions', True)
    transcript.cond_counter += 2 # each time, two are used
    transcript.instructions_counter += 2 # each time, two are used
    ret = transcriptor_dict['COND'](cond_to_rgb.cond_name_counter)
    cond_to_rgb.cond_name_counter += 1
    return ret


var_to_rgb.var_name_counter = 0
body_to_rgb.body_name_counter = 0
cond_to_rgb.cond_name_counter = 0


@addToClass(AST.ProgramNode)
def transcript(self):
    ret = ''
    for c in self.children:
        trans = c.transcript()
        if c.type == 'if else':
            # TODO ca rajoute un pass à chaque fois, faire en sorte de n'en rajouter que quand c'est nécessaire (else est la dernière instruction du bloc)
            trans += f"{transcriptor_dict['PASS']}\n"
        ret += trans
    return ret

@addToClass(AST.TokenNode)
def transcript(self):
    if isinstance(self.tok, str):
        x = transcriptor_dict['PUSHV']
        v = var_to_rgb(self.tok)
        # transcript.var_counter += 1 added in var_to_rgb
    else:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(self.tok)
        # transcript.const_counter += 1 added in num_to_rgb

    transcript.instructions_counter += 1
    return f"{x}\n{v}\n"

@addToClass(AST.OpNode)
def transcript(self):
    args = [c.transcript() for c in self.children]
    if len(args) == 1:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(0)

        # transcript.const_counter += 1 added in num_to_rgb
        transcript.instructions_counter += 1 # PUSHC
        args.insert(0, f"{x}\n{v}\n")

    transcript.instructions_counter += 1 # operation
    return reduce(operations[self.op], args)

@addToClass(AST.AssignNode)
def transcript(self):
    ret = self.children[1].transcript()

    x = transcriptor_dict['SET']
    v = var_to_rgb(self.children[0].tok)

    # transcript.var_counter += 1 added in var_to_rgb
    transcript.instructions_counter += 1

    ret += f"{x}\n{v}\n"
    
    return ret

@addToClass(AST.PrintNode)
def transcript(self):
    ret = self.children[0].transcript()

    x = transcriptor_dict['PRINT']
    transcript.instructions_counter += 1

    ret += f"{x}\n"

    return ret

@addToClass(AST.WhileNode)
def transcript(self):

    jmp = transcriptor_dict['JMP']
    cond = cond_to_rgb()
    body = body_to_rgb()
    jinz = transcriptor_dict['JINZ']
    
    ret = f"{jmp}\n{cond}\n"
    ret += f"{body}\n"
    ret += self.children[1].transcript()

    ret += f"{cond}\n"
    ret += self.children[0].transcript()
    ret += f"{jinz}\n{body}\n"


    transcript.instructions_counter += 2 # one jump, one jinz

    return ret


@addToClass(AST.IfNode)
def transcript(self):
    
    jmp = transcriptor_dict['JMP']
    jinz = transcriptor_dict['JINZ']
    cond = cond_to_rgb()
    body = body_to_rgb()
    endif = cond_to_rgb()
    
    ret = f"{jmp}\n{cond}\n"
    ret += f"{body}\n"
    ret += self.children[1].transcript()
    ret += f"{jmp}\n{endif}\n"

    ret += f"{cond}\n"
    ret += self.children[0].transcript()
    ret += f"{jinz}\n{body}\n"
    
    ret += f"{endif}\n"

    transcript.instructions_counter += 3 # two jump, one jinz

    return ret

@addToClass(AST.IfElseNode)
def transcript(self):
   
    jmp = transcriptor_dict['JMP']
    jinz = transcriptor_dict['JINZ']
    cond = cond_to_rgb()
    body = body_to_rgb()
    endif = cond_to_rgb()
    
    ret = f"{jmp}\n{cond}\n"
    ret += f"{body}\n"
    ret += self.children[1].transcript()
    ret += f"{jmp}\n{endif}\n"

    ret += f"{cond}\n"
    ret += self.children[0].transcript()
    ret += f"{jinz}\n{body}\n"
    
    ret += self.children[2].transcript()
    
    ret += f"{endif}\n"

    transcript.instructions_counter += 3 # two jump, one jinz

    return ret


transcript.var_counter = 0
transcript.instructions_counter = 0
transcript.const_counter = 0
transcript.body_counter = 0
transcript.cond_counter = 0
transcript.if_counter = 0

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
    #print(f'row, column {row}, {column}')
    column += 1
    if column >= array.shape[0]:
        column = 0
        row += 1
    return row, column

def controle_size(image):
    '''size: total pixels needed '''
    required_size = (transcript.instructions_counter * MAX_INSTRUCTIONS_BIT_SIZE
    + transcript.var_counter   * MAX_VAR_BIT_SIZE
    + transcript.const_counter * MAX_NUM_BIT_SIZE
    + transcript.body_counter  * MAX_BODIES_BIT_SIZE
    + transcript.cond_counter * MAX_CONDITIONS_BIT_SIZE)

    # print(f'instr nb {transcript.instructions_counter}')
    # print(f'var nb {transcript.var_counter}')
    # print(f'const nb {transcript.const_counter}')
    # print(f'body nb {transcript.body_counter}')
    # print(f'cond nb {transcript.cond_counter}\n')

    # how much pixels are needed
    required_size += MAX_INSTRUCTIONS_BIT_SIZE # add the EMPTY operator at the end
    # print(f'required size {required_size}')
    required_size = int(required_size / 3 + 1)

    image_size = image.shape[0] * image.shape[1]
    print(f'{required_size} pixels are needed, image has {image_size} pixels')

    if (image_size < required_size):
        print(f'the image has only {image_size} pixels')
        exit(0)
    
def change_bit(bit, image, row_counter, column_counter, rgb_counter):
    '''rgb_value is {2, 1, 0} in rgb (...[2] means red value of pixel)'''
    #print(row_counter, column_counter, rgb_counter)
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
    
    print(s)
    instructions = s.split('\n')[:-1] # remove last line (always empty line)
    import cv2
    image = cv2.imread(source_image_path, cv2.IMREAD_COLOR)
    
    controle_size(image)

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

        was_a_num = instruction == transcriptor_dict['NUM'](0)[0]
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
was_last_operation_a_endif = False


def decode(code_rgb):
    '''headhache assured on this function'''

    global was_last_operation_linked_with_body_or_cond
    global was_last_operation_a_var
    global was_last_operation_a_num
    global was_last_operation_a_body
    global was_last_operation_a_cond
    global was_last_operation_a_endif

    # false when you have to add : and no \n to the line
    # true for the inverse
    # ex.
    # body0: PUSHC 3\n    # false
    # JINZ body0\n        # true
    old_was_last_operation_linked_with_body_or_cond = was_last_operation_linked_with_body_or_cond
    if code_rgb != transcriptor_dict['BODY'](0)[0] and code_rgb != transcriptor_dict['COND'](0)[0]:
        was_last_operation_linked_with_body_or_cond = (
            code_rgb == transcriptor_dict['JMP']
            or code_rgb == transcriptor_dict['JINZ'])

    #print(f'{old_was_last_operation_linked_with_body_or_cond} when {inv_transcriptor_dict[code_rgb] if can_invert(code_rgb) else code_rgb}')

    if code_rgb == transcriptor_dict['VAR'](0)[0]:
        was_last_operation_a_var = True
        return ' ', False

    elif was_last_operation_a_var:
        was_last_operation_a_var = False
        return f'var{code_rgb}', True
    
    elif code_rgb == transcriptor_dict['NUM'](0)[0]:
        was_last_operation_a_num = True
        return ' ', False

    elif was_last_operation_a_num:
        was_last_operation_a_num = False
        return f'{code_rgb}', True
    
    elif code_rgb == transcriptor_dict['BODY'](0)[0]:
        was_last_operation_a_body = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False
    
    elif was_last_operation_a_body:
        was_last_operation_a_body = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'body{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond

    elif code_rgb == transcriptor_dict['COND'](0)[0]:
        was_last_operation_a_cond = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False
    
    elif was_last_operation_a_cond:
        was_last_operation_a_cond = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'cond{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond


    was_last_operation_a_var = code_rgb == transcriptor_dict['VAR']
    was_last_operation_a_num = code_rgb == transcriptor_dict['NUM']

    should_new_line = not (
        code_rgb == transcriptor_dict['PUSHC']
        or code_rgb == transcriptor_dict['PUSHV']
        or code_rgb == transcriptor_dict['SET']
        or code_rgb == transcriptor_dict['JMP']
        or code_rgb == transcriptor_dict['JINZ']
        or code_rgb == transcriptor_dict['JIZ'])
    
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
            #print(x)
            rgb_counter += 1
            if rgb_counter == 3:
                rgb_counter = 0
                row_counter, column_counter = increment(row_counter, column_counter, image_array)
        
        code_as_bit = bit_array_to_int(x)
        print(code_as_bit)
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
        #os.remove(opcode_filename)
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
