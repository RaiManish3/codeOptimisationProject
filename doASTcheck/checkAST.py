#-----------------------------------------------------------------
# pycparser: checkAST.py
#
# Using pycparser scanning C file, looking for sensitive patterns
# and storing their information in a file.
#
# Manish Rai
#-----------------------------------------------------------------
from __future__ import print_function
import sys
import itertools

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
sys.path.extend(['.', '..'])

from pycparser import c_parser, c_ast, parse_file

#globals
#dictionary mapping class types to line range in initialPattern file
classMap = {'FuncCall':(2,9)}
file_initialPattern = "initialPattern.txt"
file_dataStore = "data.txt"
line_offset = []
ParamStore = []
IdentifierStore = []

#####################################################################################################
def build_pattern_AST(pattern_string):
    parser = c_parser.CParser()
    ast = parser.parse(pattern_string)
    return ast

#####################################################################################################
def ArrayDecl_nodeCheck(pattern_node, file_node):
    return True

def ArrayRef_nodeCheck(pattern_node, file_node):
    return True

def Assignment_nodeCheck(pattern_node, file_node):
    return True

def BinaryOp_nodeCheck(pattern_node, file_node):
    flag = False
    if pattern_node.op == file_node.op:
        x = pattern_node.left
        y = file_node.left
        if type(x).__name__ == type(y).__name__:
            what_type = type(x).__name__
            flag = eval(what_type+"_nodeCheck(x, y)")
        x = pattern_node.right
        y = file_node.right
        if type(x).__name__ == type(y).__name__:
            what_type = type(x).__name__
            flag = eval(what_type+"_nodeCheck(x, y)")
    return flag

def Break_nodeCheck(pattern_node, file_node):
    return True

def Cast_nodeCheck(pattern_node, file_node):
    return True

def Compound_nodeCheck(pattern_node, file_node):
    return True

def CompoundLiteral_nodeCheck(pattern_node, file_node):
    return True

def Constant_nodeCheck(pattern_node, file_node):
    return True

def Continue_nodeCheck(pattern_node, file_node):
    return True

def Decl_nodeCheck(pattern_node, file_node):
    return True

def DeclList_nodeCheck(pattern_node, file_node):
    return True

def Default_nodeCheck(pattern_node, file_node):
    return True

def DoWhile_nodeCheck(pattern_node, file_node):
    return True

def EllipsisParam_nodeCheck(pattern_node, file_node):
    return True

def EmptyStatement_nodeCheck(pattern_node, file_node):
    return True

def Enum_nodeCheck(pattern_node, file_node):
    return True

def Enumerator_nodeCheck(pattern_node, file_node):
    return True

def EnumeratorList_nodeCheck(pattern_node, file_node):
    return True

def ExprList_nodeCheck(pattern_node, file_node):
    flag = True
    try:
        tmp = zip(pattern_node.children(),file_node.children())
        for (xname, x), (yname, y) in tmp:
            if (type(x).__name__ == type(y).__name__ or x.name.startswith('param')) and flag:
                what_type = type(y).__name__
                flag = eval(what_type+"_nodeCheck(x, y)")
            else:
                return False
    except:
        return False
    return True

def For_nodeCheck(pattern_node, file_node):
    return True

def FuncCall_nodeCheck(pattern_node, file_node):
    if type(pattern_node).__name__== 'ID' and pattern_node.name.startswith('param'):
        n = int(pattern_node.name[5:].strip())
        if len(ParamStore) <= n:
            #store the function as a parameter
            pass
    else:
        flag = ID_nodeCheck(pattern_node.children()[0][1], file_node.children()[0][1]) and ExprList_nodeCheck(pattern_node.children()[1][1], file_node.children()[1][1])
    return flag

def FuncDecl_nodeCheck(pattern_node, file_node):
    return True

def Goto_nodeCheck(pattern_node, file_node):
    return True

def ID_nodeCheck(pattern_node, file_node):
    if pattern_node.name == file_node.name or pattern_node.name.startswith('param'):
        if pattern_node.name.startswith('param'):
            n=int(pattern_node.name[5:].strip())
            if len(ParamStore)<=n:
                ParamStore.append(file_node.name.strip())
        return True
    return False

def IdentifierType_nodeCheck(pattern_node, file_node):
    if len(IdentifierStore)<= int(pattern_node.name[10:].strip()):
        IdentifierStore.append(file_node.type.type.names)

def If_nodeCheck(pattern_node, file_node):
    return True

def InitList_nodeCheck(pattern_node, file_node):
    return True

def UnaryOp_nodeCheck(pattern_node, file_node):
    flag = False
    if pattern_node.op == file_node.op:
        x = pattern_node.expr
        y = file_node.expr
        if type(x).__name__ == 'ID' and type(y).__name__== 'Typename':
            if x.name.startswith('identifier'):
                IdentifierType_nodeCheck(x,y)
    return flag


def Typename_nodeCheck(pattern_node, file_node):
    flag = False
    # other parameters I currently not aware of so not implementing
    x = pattern_node.type
    y = file_node.type
    if type(x).__name__ == type(y).__name__:
        what_type = type(x).__name__
        flag = eval(what_type+"_nodeCheck(x, y)")

def TypeDecl_nodeCheck(pattern_node, file_node):
    flag = False
    # other parameters I currently not aware of so not implementing
    x = pattern_node.type
    y = file_node.type
    if type(x).__name__ == type(y).__name__:
        what_type = type(x).__name__
        flag = eval(what_type+"_nodeCheck(x, y)")


#####################################################################################################
## class iterators which find the required class range in initialPattern file
def FuncCall_iterator(node):
    start_line = line_offset[classMap['FuncCall'][0]-1]
    end_line = line_offset[classMap['FuncCall'][1]-1]
    f=open(file_initialPattern,'r')
    f.seek(start_line)
    offset=0
    changeMade = False
    line='initialSet'
    while offset <= end_line - start_line and line:
        line = f.readline()
        offset+=len(line)
        #extract the name attribute
        try:
            if 'name' in line.split(',')[0].strip():
                node_name = line.split()[-1].strip()
                line = f.readline()
                offset+=len(line)
                if node_name == node.name.name:
                    line = f.readline()
                    offset+=len(line)
                    pattern_string='int f(){\n'
                    while 'end:' not in line:
                        pattern_string+=line
                        line = f.readline()
                        offset+=len(line)
                    pattern_string+='}'
                    pattern_ast = build_pattern_AST(pattern_string)
                    #travel down to the compound element
                    pattern_ast = pattern_ast.ext[0].children()[1][1].children()
                    flag = FuncCall_nodeCheck(pattern_ast[0][1], node)
                    if flag:
                        changeMade = True
                        print(ParamStore)
                        print(IdentifierStore)
                        print(node.coord.line, node.coord.column)
                        """
                        fd = open(file_dataStore,'a')
                        fd.write(str(ParamStore)+'\n')
                        fd.close()
                        """
                        ParamStore[:]=[]
                        IdentifierStore[:]=[]
        except:
            pass

    return changeMade
    f.close()

#####################################################################################################
def dfs_node_iterate(node):
    for xname, x in node.children():
        what_type = type(x).__name__
        changeMade = False
        if what_type in classMap:
            #invoke the respective type check function
            changeMade = eval(what_type+"_iterator(eval('x'))")
        #Do not iterate again on parts whose children had the changes
        if not changeMade:
            dfs_node_iterate(x)

#generate the AST for the C program and does a DFS on it
def check(filename):
    ast = parse_file(filename, use_cpp=True)
    dfs_node_iterate(ast)                               # implement dfs here


#####################################################################################################
#loads the file just one time and makes a list of offset
def loadfileOptimised():
    global file_initialPattern
    f = open(file_initialPattern,'r')
    offset = 0
    for line in f.readlines():
        line_offset.append(offset)
        offset += len(line)
        f.seek(0)
    f.close()
    # Now, to skip to line n (with the first line being line 0), just do
    #file.seek(line_offset[n])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'sample.c'

    loadfileOptimised()
    check(filename)
