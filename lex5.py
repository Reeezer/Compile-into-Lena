import ply.lex as lex

#These words can't be used other then their orignal purpose.
reserved_words = (
	'while',
	'print',
	'if',
	'else',
	'function'
)

#These words can't be used other then their orignal purpose.
tokens = (
	'NUMBER',
	'CHAR',
	'STRING',
	'ADD_OP',
	'MUL_OP',
	'MOD',
	'POW',
	'IDENTIFIER',
) + tuple(map(lambda s: s.upper(), reserved_words))

literals = '();={}'


def t_ADD_OP(t):
	r'[+-]'
	return t

def t_MOD(t):
	r'[%]'
	return t

def t_POW(t):
	r'[\^]'
	return t
	
def t_MUL_OP(t):
	r'[*/]'
	return t

def t_NUMBER(t):
	r'\d+(\.\d+)?'
	try:
		t.value = float(t.value)    
	except ValueError:
		print ("Line %d: Problem while parsing %s!" % (t.lineno,t.value))
		t.value = 0
	return t

def t_CHAR(t):
	r'\'[\w\s]\''
	t.value = t.value[1:-1] # remove the ' '
	return t
	
def t_ILLEGAL_CHAR(t):
	r'\'[\w\s]+\''
	print(f'ERROR: character with multiple chars: {t.value}')
	exit(-1)

def t_STRING(t):
	r'"[\w\s]+"'
	t.value = t.value[1:-1] # remove the " "
	return t

def t_IDENTIFIER(t):
	r'[A-Za-z_]\w*'
	if t.value in reserved_words:
		t.type = t.value.upper()
	return t
	
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

t_ignore  = ' \t'

def t_error(t):
	print ("Illegal character [%s]" % repr(t.value[0]))
	t.lexer.skip(1)

lex.lex()

if __name__ == "__main__":
	import sys
	prog = open(sys.argv[1]).read()

	lex.input(prog)

	while 1:
		tok = lex.token()
		if not tok: break
		print ("line %d: %s (%s)" % (tok.lineno, tok.type, tok.value))
