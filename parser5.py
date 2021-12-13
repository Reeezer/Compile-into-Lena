import ply.yacc as yacc
import math

from lex5 import tokens

import AST

operations = {
	'+' : lambda x,y: x+y,
	'-' : lambda x,y: x-y,
	'*' : lambda x,y: x*y,
	'/' : lambda x,y: x/y,
	'%' : lambda x,y: math.fmod(x,y),
	'^' : lambda x,y: math.pow(x,y),
}

vars = {}

def p_programme_statement(p):
	''' programme : statement ';' '''
	p[0] = AST.ProgramNode(p[1])

def p_programme_recursive(p):
	''' programme : statement ';' programme'''
	p[0] = AST.ProgramNode([p[1]]+p[3].children)

def p_statement(p):
	''' statement : assignation
		| structure'''
	p[0] = p[1]

def p_statement_print(p):
	'''statement : PRINT expression'''
	p[0] = AST.PrintNode(p[2])
	
def p_while_structure(p):
	"""structure : WHILE expression '{' programme '}'"""
	p[0] = AST.WhileNode((p[2], p[4]))

def p_if_structure(p):
	"""structure : IF expression '{' programme '}'
		| IF expression '{' programme '}' ';' ELSE '{' programme '}'"""
	if len(p) == 6:
		p[0] = AST.IfNode((p[2], p[4]))
	elif len(p) == 11:
		p[0] = AST.IfElseNode((p[2], p[4], p[9]))

def p_function_name(p):
	"""function_name : IDENTIFIER '(' ')'"""
	p[0] = AST.TokenNode(p[1])

def p_function_declaration(p):
	"""structure : FUNCTION function_name '{' programme '}'"""
	p[0] = AST.FunctionDeclarationNode((p[2], p[4]))

def p_function_call(p):
	"""structure : function_name"""
	p[0] = AST.FunctionCallNode(p[1])

def p_expression_op(p):
	'''expression : expression ADD_OP expression
			| expression MUL_OP expression
			| expression MOD expression
			| expression POW expression'''
	p[0] = AST.OpNode(p[2], [p[1], p[3]])
	
def p_expression_num_or_var(p):
	'''expression : NUMBER
		| IDENTIFIER '''
	p[0] = AST.TokenNode(p[1])
	
def p_expression_paren(p):
	'''expression : '(' expression ')' '''
	p[0] = p[2]
	
def p_minus(p):
	''' expression : ADD_OP expression %prec UMINUS'''
	p[0] = AST.OpNode(p[1], [p[2]])
	
def p_assign(p):
	''' assignation : IDENTIFIER '=' expression '''
	p[0] = AST.AssignNode([AST.TokenNode(p[1]),p[3]])

def p_error(p):
	print ("Syntax error in line %d" % p.lineno)
	yacc.errok()

precedence = (
	('left', 'ADD_OP'),
	('left', 'MUL_OP'),
	('right', 'UMINUS'),  
)

yacc.yacc(outputdir='generated')

def parse(program):
	return yacc.parse(program)

if __name__ == "__main__":
	import sys 
	
	prog = open(sys.argv[1]).read()
	ast = yacc.parse(prog)
	print (ast)
	
	import os
	os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
	graph = ast.makegraphicaltree()
	name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
	graph.write_pdf(name) 
	print ("wrote ast to", name)
	