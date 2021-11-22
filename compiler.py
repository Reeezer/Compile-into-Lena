import AST
from AST import addToClass
from functools import reduce

operations = {
    '+': lambda x,y: f'{x}{y}ADD\n',
    '-': lambda x,y: f'{x}{y}SUB\n',
    '*': lambda x,y: f'{x}{y}MUL\n',
    '/': lambda x,y: f'{x}{y}DIV\n',
}

@addToClass(AST.ProgramNode)
def compile(self):
    ret = ''
    for c in self.children:
        ret += c.compile()
    return ret

@addToClass(AST.TokenNode)
def compile(self):
    if isinstance(self.tok, str):
            return f'PUSHV {self.tok}\n'
    
    return f'PUSHC {self.tok}\n'

@addToClass(AST.OpNode)
def compile(self):
    args = [c.compile() for c in self.children]
    if len(args) == 1:
        args.insert(0, 'PUSHC 0\n')

    return reduce(operations[self.op], args)

@addToClass(AST.AssignNode)
def compile(self):
    ret = self.children[1].compile()
    ret += f'SET {self.children[0].tok}\n'
    
    return ret

@addToClass(AST.PrintNode)
def compile(self):
    ret = self.children[0].compile()
    ret += 'PRINT\n'

    return ret

@addToClass(AST.WhileNode)
def compile(self):
    counter = compile.whileFlag
    compile.whileFlag += 1

    ret = f'JMP cond{counter}\n'
    ret += f'body{counter}: '
    ret += self.children[1].compile()

    ret += f'cond{counter}: '
    ret += self.children[0].compile()
    ret += f'JINZ body{counter}\n'

    return ret

compile.whileFlag = 0

def main():
    from parser5 import parse
    import sys, os

    prog = open(sys.argv[1]).read()
    ast = parse(prog)

    compiled = ast.compile()

    name = os.path.splitext(sys.argv[1])[0] + '.vm'
    outfile = open(name, 'w')
    outfile.write(compiled)
    outfile.close()
    
    print(f'Wrote output to {name}')

if __name__ == '__main__':
    main()