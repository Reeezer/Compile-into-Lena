'''
Authors:

    Campana Luca
    Muller Leon
    Girardin Jarod

Date:
    14.01.2022

Usage:
    -g
    Generate a runnable image from a code written in CALL21 (Custom Assembly Lesson Language 2021)

    -r
    Run a runnable image
'''

from re import T
import AST
from AST import addToClass
from functools import reduce
from ast import literal_eval as string_to_tuple
from math import log


# dict storing all the instructions, and their following "rgb" code
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
    'MOD'  : 13,
    'POW'  : 14,
    'PASS' : 15,
    'VAR'  : lambda x: (16, x),  # the size is MAX_INSTRUCTIONS + MAX_VAR
    'NUM'  : lambda x: (17, x),  # the size is MAX_INSTRUCTIONS + MAX_NUM
    'BODY' : lambda x: (18, x), # the size is MAX_INSTRUCTIONS + MAX_BODY
    'COND' : lambda x: (19, x), # the size is MAX_INSTRUCTIONS + MAX_COND
    'STR'  : lambda x: (20, len(x), string_as_int(x)), # the size is MAX_INSTRUCTIONS + MAX_NUM + CHAR_LENGTH*len(x)
    'PUSHS': 21
}

def can_invert(key):
    try:
        tuple(key)
        return True
    except Exception:
        return False


# reversed dict, use for executing a picture
inv_transcriptor_dict = {v: k for k, v in transcriptor_dict.items() if can_invert(k)}

# manually add the lambdas
inv_transcriptor_dict[16] = 'VAR'
inv_transcriptor_dict[17] = 'NUM'
inv_transcriptor_dict[18] = 'BODY'
inv_transcriptor_dict[19] = 'COND'
inv_transcriptor_dict[20] = 'STR'

# thoses MAX means "how much memory is allowed for each thing"
# meaning for a MAX_VAR_BIT_SIZE of 26 each variable will use 26/3 pixels
# and also a maximum of 67108864 differents variables
# 8 would mean maximum 256 instructions
# 3 would mean 8 differents var

MAX_INSTRUCTIONS_BIT_SIZE = int(log(len(transcriptor_dict), 2) +1)

MAX_VAR_BIT_SIZE = 8
# 5 would mean numeric values goes from -32 to 32
# negatives computed as 0 minus positive (-x = 0-abs(x))
MAX_NUM_BIT_SIZE = 8

# means the string can have max 4095 characters (2**12 -1), -1 because of the empty string ""
MAX_STRING_LENGTH_BIT_SIZE = 12

MAX_CONDITIONS_BIT_SIZE = 8

MAX_BODIES_BIT_SIZE = 8

# using the whole ascii table => 128 bits, or 2**7
CHAR_BIT_SIZE = 7

operations = {
    '+': lambda x,y: f"{x}{y}{transcriptor_dict['ADD']}\n",
    '-': lambda x,y: f"{x}{y}{transcriptor_dict['SUB']}\n",
    '*': lambda x,y: f"{x}{y}{transcriptor_dict['MUL']}\n",
    '/': lambda x,y: f"{x}{y}{transcriptor_dict['DIV']}\n",
    '%': lambda x,y: f"{x}{y}{transcriptor_dict['MOD']}\n",
    '^': lambda x,y: f"{x}{y}{transcriptor_dict['POW']}\n",
}

func = {}
func_unused = set()
vars = {}
vars_unused = set()

var_scope = {} # dict of dict: access to function's scope, and then variable's scope (in the given function)
var_scope['main'] = {}
current_scope = {} # dict: access to current scope of a given function
current_scope['main'] = 0

def verify_limits(value, limit, error):
    p = pow(2, limit) -1
    if value > p:
        raise Exception(f'{error}\ncurrent: {value}, max: {p}')

def verify_chars_are_ascii(s):
    for c in s:
        if ord(c) > 127:
            raise Exception(f'{c} is not an ASCII character\nin string {s}')

def var_to_rgb(var):
    transcript.var_counter += 1
    transcript.instructions_counter += 1

    if var in vars.keys():
        if var in vars_unused:
            vars_unused.remove(var)
        return vars[var]
    
    verify_limits(var_to_rgb.var_name_counter, MAX_VAR_BIT_SIZE, 'too much var')
    
    x = transcriptor_dict['VAR'](var_to_rgb.var_name_counter)
    var_to_rgb.var_name_counter += 1
    vars[var] = x
    vars_unused.add(var)

    return x


# those two functions are not used, but mentionned in the report
# # https://stackoverflow.com/questions/14431170/get-the-bits-of-a-float-in-python
# def floatToBits(f):
#     import struct
#     s = struct.pack('>f', f)
#     return struct.unpack('>l', s)[0]

# def bitsToFloat(b):
#     import struct
#     s = struct.pack('>l', b)
#     return struct.unpack('>f', s)[0]

# transform a numeric value to a the value used to store into the picture
def num_to_rgb(num):
    # use False if numbers are unsigned, actually -127 is computed as 0- (+127) so only positive are concidered for now
    # verify_limits(num, MAX_NUM_BIT_SIZE, 'number too big or too short', False)
    verify_limits(num, MAX_NUM_BIT_SIZE, 'number too big or too short')
    x = int(num)
    transcript.const_counter += 1
    transcript.instructions_counter += 1
    return transcriptor_dict['NUM'](x)

# same, but for a body
def body_to_rgb():
    verify_limits(body_to_rgb.body_name_counter, MAX_BODIES_BIT_SIZE, 'too much bodies')
    transcript.body_counter += 2 # each time, two are used
    transcript.instructions_counter += 2 # each time, two are used
    ret = transcriptor_dict['BODY'](body_to_rgb.body_name_counter)
    body_to_rgb.body_name_counter += 1
    return ret

# same, but for a cond
def cond_to_rgb():
    verify_limits(cond_to_rgb.cond_name_counter, MAX_CONDITIONS_BIT_SIZE, 'too much conditions')
    transcript.cond_counter += 2 # each time, two are used
    transcript.instructions_counter += 2 # each time, two are used
    ret = transcriptor_dict['COND'](cond_to_rgb.cond_name_counter)
    cond_to_rgb.cond_name_counter += 1
    return ret

# same, but for a string
def string_to_rgb(s):
    verify_chars_are_ascii(s)
    verify_limits(len(s), MAX_STRING_LENGTH_BIT_SIZE, 'string too long')
    transcript.instructions_counter += 1
    transcript.string_counter += 1
    transcript.char_counter += len(s)
    ret = transcriptor_dict['STR'](s)
    return ret

def string_as_int(s):
    '''change a string into an int
    used to store into the picture'''
    ret = []
    for c in s:
        ret.append(ord(c))
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
        current_func_name = transcript.current_func
        var_name = self.tok
        
        if current_func_name != 'main': # Actually in a function's scope
            var_name = f"{current_func_name}_{var_name}"

        if var_name not in var_scope[current_func_name] or var_scope[current_func_name][var_name] > current_scope[current_func_name]:
            error_exit(f"Scope is not being respected for variable '{var_name}' in function '{current_func_name}'")

        x = transcriptor_dict['PUSHV']
        v = var_to_rgb(var_name)
    else:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(self.tok)

    transcript.instructions_counter += 1
    
    return f"{x}\n{v}\n"


@addToClass(AST.StringNode)
def transcript(self):
    x = transcriptor_dict['PUSHS']
    v = string_to_rgb(self.tok)
    
    transcript.instructions_counter += 1
    return f"{x}\n{v}\n"


@addToClass(AST.OpNode)
def transcript(self):
    args = [c.transcript() for c in self.children]
    if len(args) == 1:
        x = transcriptor_dict['PUSHC']
        v = num_to_rgb(0)

        transcript.instructions_counter += 1 # PUSHC
        args.insert(0, f"{x}\n{v}\n")

    transcript.instructions_counter += 1 # operation
    return reduce(operations[self.op], args)

@addToClass(AST.AssignNode)
def transcript(self):
    ret = self.children[1].transcript()
    
    current_func_name = transcript.current_func
    var_name = self.children[0].tok

    if current_func_name != 'main': # Actually in a function's scope
        var_name = f"{current_func_name}_{var_name}"

    if var_name not in var_scope[current_func_name] or var_scope[current_func_name][var_name] > current_scope[current_func_name]:
        var_scope[current_func_name][var_name] = current_scope[current_func_name]

    x = transcriptor_dict['SET']
    v = var_to_rgb(var_name)

    self.children[0].tok = var_name

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
    current_scope[transcript.current_func] += 1

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

    current_scope[transcript.current_func] -= 1

    transcript.instructions_counter += 2 # one jump, one jinz

    return ret

@addToClass(AST.IfNode)
def transcript(self):
    current_scope[transcript.current_func] += 1
    
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

    current_scope[transcript.current_func] -= 1

    transcript.instructions_counter += 3 # two jump, one jinz

    return ret

@addToClass(AST.IfElseNode)
def transcript(self):
    current_scope[transcript.current_func] += 1
   
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

    current_scope[transcript.current_func] -= 1

    transcript.instructions_counter += 3 # two jump, one jinz

    return ret

@addToClass(AST.FunctionDeclarationNode)
def transcript(self):
    func_name = str(self.children[0])[:-1]
    func_name = func_name[1:-1]

    if current_scope['main'] > 0:
        error_exit(f"Function {func_name} has to be declared as global")
    if func_name in func:
        error_exit(f"Function {func_name} can't be overrided")
    
    current_scope[func_name] = 0
    var_scope[func_name] = {}
    
    func[func_name] = self.children[1] # Because we need to increase the flag on each call, then we store the function declaration, and paste it on the call
    
    func_unused.add(func_name)
    
    return ""

@addToClass(AST.FunctionCallNode)
def transcript(self):
    func_name = str(self.children[0])[:-1]
    func_name = func_name[1:-1]

    transcript.current_func = func_name
    current_scope[func_name] += 1

    ret = func[func_name].transcript()
    
    current_scope[func_name] -= 1
    transcript.current_func = 'main'

    if func_name in func_unused:
        func_unused.remove(func_name)
    
    return ret

transcript.var_counter = 0
transcript.instructions_counter = 0
transcript.const_counter = 0
transcript.body_counter = 0
transcript.cond_counter = 0
transcript.current_func = 'main'
transcript.string_counter = 0
transcript.char_counter = 0

arg_generate = '-g'
arg_run = '-r'

def get_instruction(instruction):
    try:
        return int(instruction) # is it an int
    except ValueError: # this is a tuple
        return string_to_tuple(instruction)

def split_into_bits(value, max_bits):
    '''split the specified value into array of bits
    those bits will be assigned to the rgb values of the pixels in the picture'''
    if type(value) == list:
        ret = []
        for v in value:
            ret += (split_into_bits(v, CHAR_BIT_SIZE))
        return ret
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
    '''used to easily increment our index trackers of the picture'''
    column += 1
    if column >= array.shape[0]:
        column = 0
        row += 1
    if row >= array.shape[1]:
        print('ERROR: code out of range of picture size')
        exit(-1)
    return row, column

def controle_size(image):
    '''verify if the picture is large enough to store the code
    size: total pixels needed'''
    required_size = (transcript.instructions_counter * MAX_INSTRUCTIONS_BIT_SIZE
    + transcript.var_counter   * MAX_VAR_BIT_SIZE
    + transcript.const_counter * MAX_NUM_BIT_SIZE
    + transcript.body_counter  * MAX_BODIES_BIT_SIZE
    + transcript.cond_counter * MAX_CONDITIONS_BIT_SIZE
    + transcript.string_counter * MAX_STRING_LENGTH_BIT_SIZE
    + transcript.char_counter * CHAR_BIT_SIZE)
    
    # how much pixels are needed
    required_size += MAX_INSTRUCTIONS_BIT_SIZE # add the EMPTY operator at the end
    # print(f'required size {required_size}')
    
    if DEBUG:
        print('\nhow much bits per thing:')
        print(f'instructions\tnb {transcript.instructions_counter}\t=> {transcript.instructions_counter * MAX_INSTRUCTIONS_BIT_SIZE}')
        print(f'var\tnb {transcript.var_counter}\t=> {transcript.var_counter * MAX_VAR_BIT_SIZE}')
        print(f'const\tnb {transcript.const_counter}\t=> {transcript.const_counter * MAX_NUM_BIT_SIZE}')
        print(f'body\tnb {transcript.body_counter}\t=> {transcript.body_counter * MAX_BODIES_BIT_SIZE}')
        print(f'cond\tnb {transcript.cond_counter}\t=> {transcript.cond_counter * MAX_CONDITIONS_BIT_SIZE}')
        print(f'str\tnb {transcript.string_counter}\t=> {transcript.string_counter * MAX_STRING_LENGTH_BIT_SIZE} (for the length indicator)')
        print(f'char\tnb {transcript.char_counter}\t=> {transcript.char_counter * CHAR_BIT_SIZE}')
        print(f'eof instruction\tnb 1\t=> {MAX_INSTRUCTIONS_BIT_SIZE}')
        print(f'\nfor a total of\t=> {required_size}\n')

    required_size = int(required_size / 3 + 1)

    image_size = image.shape[0] * image.shape[1]
    print(f'{required_size} pixels are needed, image has {image_size} pixels')

    if (image_size < required_size):
        error_exit(f'The image has only {image_size} pixels')
    
def change_bit(bit, image, row_counter, column_counter, rgb_counter):
    '''change the less-valuable bit of the picture, on the specified pixel, on the specified r, g or b value
    rgb_value is {2, 1, 0} in rgb (...[2] means red value of pixel)'''
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
    
    controle_size(image)

    column_counter = 0
    row_counter = 0
    rgb_counter = 0

    for instruction in instructions: # instruction is str
        instruction = get_instruction(instruction)
        value = None
        string = None
        if (type(instruction) is tuple):
            if len(instruction) == 3:
                string = instruction[2]
            value = instruction[1]
            instruction = instruction[0]
               


        for bit in split_into_bits(instruction, MAX_INSTRUCTIONS_BIT_SIZE):
            row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
                
        was_a_num = instruction == transcriptor_dict['NUM'](0)[0]
        was_a_string = instruction == transcriptor_dict['STR']('')[0]
        
        # Usefull for debug   
        if DEBUG:
            print(f'__________________________________________________')
            insctruction_name = inv_transcriptor_dict[instruction] if instruction in inv_transcriptor_dict.keys() else 'SPECIAL INSTRUCTION'
            print(f'{instruction}\tinstruction: {insctruction_name}')
            print(f'\t{split_into_bits(instruction, MAX_INSTRUCTIONS_BIT_SIZE)}')
            if value is not None:
                if was_a_string:
                    print(f'{value}\tlen of string')
                    print(f'\t{split_into_bits(value, MAX_STRING_LENGTH_BIT_SIZE)}')
                    print(f'{string}\tstring')
                    print(f'\t{split_into_bits(string, CHAR_BIT_SIZE*value)}')
                else:
                    size_to_convert = MAX_NUM_BIT_SIZE if was_a_num else MAX_VAR_BIT_SIZE
                    print(f'{value}\tvalue')
                    print(f'\t{split_into_bits(value, size_to_convert)}')


        # add var id or num value
        if value is not None:
                if was_a_string:
                    for bit in split_into_bits(value, MAX_STRING_LENGTH_BIT_SIZE):
                        row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
                    for bit in split_into_bits(string, CHAR_BIT_SIZE*value):
                        row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
                else:
                    size_to_convert = MAX_NUM_BIT_SIZE if was_a_num else MAX_VAR_BIT_SIZE
                    for bit in split_into_bits(value, size_to_convert):
                        row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)


    # apply "EOF"
    for bit in split_into_bits(transcriptor_dict['EMPTY'], MAX_INSTRUCTIONS_BIT_SIZE):
        row_counter, column_counter, rgb_counter = change_bit(bit, image, row_counter, column_counter, rgb_counter)
        
    cv2.imwrite(output_image_path, image)


def bit_array_to_int(arr):
    arr.reverse()
    x = 0
    for i in range(len(arr)):
        x += arr[i] * pow(2, i)
    return x
    

def bit_array_to_str(arr):
    arr.reverse()
    s = ''
    for i in range(0, len(arr), CHAR_BIT_SIZE):
        x = 0
        for j in range(CHAR_BIT_SIZE):
            x += arr[j+i] * pow(2, j)
        s += chr(x)
    return s[::-1]

was_last_operation_linked_with_body_or_cond = False
was_last_instruction_var = False
was_last_instruction_num = False
was_last_instruction_body = False
was_last_instruction_cond = False
was_last_instruction_str_part_1 = False
was_last_instruction_str_part_2 = False


def decode(code_rgb):
    '''headhache assured on this function
    it will decode the actual code stored inside the pixels of the picture
    
    depending on which last instruction was used, il will interprete differently the value
    
    ex. code is 21 => could be an instruction, a numeric value, a variable, etc
    
    return the string to add in the "assembly" file, along with a boolean
    the boolean says if you have to new line after the string, or keep writing on the same line
    
    ex:
    PUSHC 3
    PRINT
    
    [0] "PUSHC", False
    [1] "3", True
    [2] "PRINT", True'''

    global was_last_operation_linked_with_body_or_cond
    global was_last_instruction_var
    global was_last_instruction_num
    global was_last_instruction_body
    global was_last_instruction_cond
    global was_last_instruction_str_part_1
    global was_last_instruction_str_part_2

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

   
    if was_last_instruction_var:
        was_last_instruction_var = False
        return f'var{code_rgb}', True
        
    elif was_last_instruction_num:
        was_last_instruction_num = False
        return f'{code_rgb}', True
        
    elif was_last_instruction_body:
        was_last_instruction_body = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'body{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond
        
    elif was_last_instruction_cond:
        was_last_instruction_cond = False
        double_dot = ':' if not old_was_last_operation_linked_with_body_or_cond else ''
        return f'cond{code_rgb}{double_dot} ', old_was_last_operation_linked_with_body_or_cond

    elif was_last_instruction_str_part_1:
        was_last_instruction_str_part_1 = False
        was_last_instruction_str_part_2 = True
        return ' ', False

    elif was_last_instruction_str_part_2:
        was_last_instruction_str_part_2 = False
        return f'{code_rgb}', True


    elif code_rgb == transcriptor_dict['VAR'](0)[0]:
        was_last_instruction_var = True
        return ' ', False
    
    elif code_rgb == transcriptor_dict['NUM'](0)[0]:
        was_last_instruction_num = True
        return ' ', False
    
    elif code_rgb == transcriptor_dict['BODY'](0)[0]:
        was_last_instruction_body = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False

    elif code_rgb == transcriptor_dict['COND'](0)[0]:
        was_last_instruction_cond = True
        return ' ' if old_was_last_operation_linked_with_body_or_cond else '', False

    elif code_rgb == transcriptor_dict['STR']('')[0]:
        was_last_instruction_str_part_1 = True
        return '', False

    should_new_line = not (
           code_rgb == transcriptor_dict['PUSHC']
        or code_rgb == transcriptor_dict['PUSHV']
        or code_rgb == transcriptor_dict['PUSHS']
        or code_rgb == transcriptor_dict['SET']
        or code_rgb == transcriptor_dict['JMP']
        or code_rgb == transcriptor_dict['JINZ']
        or code_rgb == transcriptor_dict['JIZ'])
    
    return inv_transcriptor_dict[code_rgb], should_new_line

def run_image(image_array):
    from svm import run

    global was_last_operation_linked_with_body_or_cond
    global was_last_instruction_var
    global was_last_instruction_num
    global was_last_instruction_body
    global was_last_instruction_cond
    global was_last_instruction_str_part_1
    global was_last_instruction_str_part_2

    code = ''

    row_counter = 0
    column_counter = 0
    rgb_counter = 0

    size_to_read = MAX_INSTRUCTIONS_BIT_SIZE

    for _ in range(image_array.shape[0] * image_array.shape[1]):
        x = []
        for _ in range(size_to_read):
            x.append(image_array[row_counter][column_counter][rgb_counter] & 0b0000_0001)
            rgb_counter += 1
            if rgb_counter == 3:
                rgb_counter = 0
                row_counter, column_counter = increment(row_counter, column_counter, image_array)
        
        if was_last_instruction_str_part_2:
            code_as_bit = bit_array_to_str(x)
        else:
            code_as_bit = bit_array_to_int(x)

        if (code_as_bit == transcriptor_dict['EMPTY']
        and not was_last_instruction_num
        and not was_last_instruction_var
        and not was_last_instruction_cond
        and not was_last_instruction_body
        and not was_last_instruction_str_part_1
        and not was_last_instruction_str_part_2):
            break

        decoded, should_new_line = decode(code_as_bit)

        if was_last_instruction_num:
            size_to_read = MAX_NUM_BIT_SIZE
        elif was_last_instruction_var:
            size_to_read = MAX_VAR_BIT_SIZE
        elif was_last_instruction_cond:
            size_to_read = MAX_CONDITIONS_BIT_SIZE
        elif was_last_instruction_body:
            size_to_read = MAX_BODIES_BIT_SIZE
        elif was_last_instruction_str_part_1:
            size_to_read = MAX_STRING_LENGTH_BIT_SIZE
        elif was_last_instruction_str_part_2:
            size_to_read = CHAR_BIT_SIZE*int(code_as_bit)
        else:
            size_to_read = MAX_INSTRUCTIONS_BIT_SIZE

        new_line = '\n' if should_new_line else ''
        code += f'{decoded}{new_line}'


    if DEBUG:
        opcode_filename = 'output.vm'
        with open(opcode_filename, 'w') as f:
            f.write(code)
        print(code)
    run(code)

def warning(container: set, message: str):
    if len(container) > 0:
        print(f"*** WARNING: {message}:")
        for x in container:
            print(f"             - {x}")
        print() 

def warnings():
    warning(func_unused, 'Those functions are not used')
    warning(vars_unused, 'Those variables are not used')

def error_exit(message: str):
    print(f"*** ERROR: {message}\n***        Exit code parsing")
    exit(-1)


def print_help_and_exit():
    s = f"""transcriptor.py {{MODE}} {{SOURCE}} {{IMAGE_SOURCE}} --debug
    HOW TO USE

    1st arg must be [{arg_generate} | {arg_run}]
    2nd arg must be the path to the code file
    3rd arg must be the path to the source image when generating
    4th arg can be --debug to show debug information

    MODE: {arg_generate}: compile the code
          {arg_run}: run the code inside an image
    ____________________________________________________

    python transcriptor.py {arg_generate} my_code.txt image_source.png
    python transcriptor.py {arg_run} my_code_picture.bmp
    ____________________________________________________

    - show each pixel in console
    python transcriptor.py {arg_generate} my_code.txt image_source.png --debug

    - keep the .mv file
    python transcriptor.py {arg_run} my_code_picture.bmp --debug
    ____________________________________________________"""
    print(s)
    exit(0)

def get_args():
    if (len(sys.argv) >= 5 and sys.argv[4].lower() == '--debug'
        or len(sys.argv) == 4 and sys.argv[3].lower() == '--debug'):
        global DEBUG
        DEBUG = True
    return sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None

DEBUG = False

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

        import os
        x = re.search("^(.+)\..+$", os.path.basename(source_image_path))
        IMAGE_EXTENSION = 'png'
        output = f'code_{x.group(1)}.{IMAGE_EXTENSION}'

        with open(file_path) as f:
            prog = f.read()
        
        ast = parse(prog)

        transcriptd = ast.transcript()
        
        warnings()
        generate_image(transcriptd, source_image_path, output)       
        
    elif mode == arg_run:
        import cv2
        print('running picture...\n')
        
        image = cv2.imread(file_path)
        run_image(image)

    else:
        print_help_and_exit()
