import AST
from AST import addToClass

@addToClass(AST.Node)
def thread(self, lastNode):
    for c in self.children:
        lastNode = c.thread(lastNode)
    lastNode.addNext(self)
    return self

@addToClass(AST.WhileNode)
def thread(self, lastNode):
    
    # manually make the recursion of children[0].thread(lastNode)
    # it is done to get the first children of condition
    isFirstLoop = True
    for c in self.children[0].children:
        lastNode = c.thread(lastNode)
        if isFirstLoop:
            isFirstLoop = False
            firstCondNode = lastNode
    lastNode.addNext(self.children[0])

    lastNode = self.children[0]
    # stop the manually made thread function
    
    lastNode.addNext(self)
    lastNode = self
    lastNode = self.children[1].thread(lastNode)
    lastNode.addNext(firstCondNode)

    return self

def thread(tree):
    entry = AST.EntryNode()
    tree.thread(entry)
    return entry

if __name__ == '__main__':
    from parser5 import parse
    import sys, os
    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    entry = thread(ast)

    graph = ast.makegraphicaltree()
    entry.threadTree(graph)

    name = os.path.splitext(sys.argv[1])[0] + '-ast-threaded.pdf'
    graph.write_pdf(name)

    print(f'wrote threaded ast to {name}')
