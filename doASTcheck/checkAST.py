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

from pycparser import c_parser, c_ast, parse_file, c_generator

##globals
#dictionary mapping class types to line range in initialPattern file
classMap = {'Assignment':(2,10), 'Decl':(12,17),'FuncCall':(19, 21)}
file_initialPattern = "initialPattern.txt"
file_dataStore = "data.txt"
line_offset = []

#information store
ParamStore = []
IdentifierStore = []
OpStore = []

#variables
param = 'param'

#####################################################################################################
def build_pattern_AST(pattern_string):
    parser = c_parser.CParser()
    ast = parser.parse(pattern_string)
    return ast

#####################################################################################################

#----------------------------------------------------------
## helper functions

def getLineRange(node):
    type_name = type(node).__name__
    start_line = line_offset[classMap[type_name][0]-1]
    end_line = line_offset[classMap[type_name][1]-1]
    return type_name, start_line, end_line

def paramID_func(x, y):
    if type(x).__name__ in ['ID','Decl'] and x.name.startswith(param):
        param_store_func(x,y)
        return True
    return False

def param_store_func(pattern_node, file_node):
    n = int(pattern_node.name[5:].strip())
    if len(ParamStore) == n:
        #store the function as a parameter
        generator = c_generator.CGenerator()
        try:
            ParamStore.append(generator.visit(file_node))
        except:
            ParamStore.append(file_node)

def identifier_store_func(pattern_node, file_node):
    for name in file_node.names:
        IdentifierStore.append(name)

def OP_store_func(pattern_node, file_node):
    OpStore.append(file_node)

def dimArray_func(file_node, frm):
    if isinstance(ParamStore[-1],list):
        ## if the caller is different, we get differnt dimensions
        ## ordering and hence we need to be specific here.
        if frm == 'decl':
            if type(file_node).__name__ == 'Constant':
                ParamStore[-1].insert(0,file_node.value)
            else:
                #assuming ID
                ParamStore[-1].insert(0,file_node.name)

        if frm == 'ref':
            if type(file_node).__name__ == 'Constant':
                ParamStore[-1].append(file_node.value)
            else:
                #assuming ID
                ParamStore[-1].append(file_node.name)
    else:
        if type(file_node).__name__ == 'Constant':
            ParamStore.append([file_node.value])
        else:
            #assuming ID
            ParamStore.append([file_node.name])

def ptr_store(file_node,times):
    if IdentifierStore==[] or not isinstance(IdentifierStore[-1], int):
        IdentifierStore.append(times)
    else:
        IdentifierStore[-1]=times

#----------------------------------------------------------

def ArrayDecl_nodeCheck(pattern_node, file_node):
    flag=False
    x, y = pattern_node.type, file_node.type
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y:
        flag = eval(type_y+"_nodeCheck(x, y)")
    elif type_y in ['ArrayDecl', 'TypeDecl']:
        ## case of multidimensional array
        flag = eval(type_y+"_nodeCheck(pattern_node, y)")

    y = file_node.dim
    type_y = type(y).__name__
    ## dimensions are to be stored always
    dimArray_func(y, 'decl')
    #print(file_node.dim_quals)
    return flag

def ArrayRef_nodeCheck(pattern_node, file_node):
    flag = False
    ## a name id guaranteed to have
    type_y = type(file_node.name).__name__
    type_x = type(pattern_node.name).__name__
    if type_x == type_y:
        flag = eval(type_y+"_nodeCheck(pattern_node.name, file_node.name)")
    else:
        flag = eval(type_y+"_nodeCheck(pattern_node, file_node.name)")

    dimArray_func(file_node.subscript, 'ref')
    return flag

def Assignment_nodeCheck(pattern_node, file_node):
    flag = False
    x, y = pattern_node, file_node
    ## some thoughts to be given here
    OP_store_func(x.op, y.op)

    x, y = pattern_node.lvalue, file_node.lvalue
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y:
        flag = eval(type_y+"_nodeCheck(x, y)")
    elif type_x in ['ArrayRef'] or type_y in ['ArrayRef']:
        flag = False
    else:
        flag = paramID_func(x,y)

    x, y = pattern_node.rvalue, file_node.rvalue
    type_x, type_y = type(x).__name__, type(y).__name__
    if flag:
        if type_x == type_y:
            flag = eval(type_y+"_nodeCheck(x, y)")
        elif type_x in ['ArrayRef'] or type_y in ['ArrayRef']:
            flag = False
        else:
            flag = paramID_func(x,y)

    return flag

# for binaryOp ::
# the operation has to be clearly defined the same as in the pattern
# the left and right if set to parameter are then set automatically
# else we dig further
def BinaryOp_nodeCheck(pattern_node, file_node):
    flag = False
    if pattern_node.op == file_node.op:

        x = pattern_node.left
        y = file_node.left
        if type(x).__name__ == type(y).__name__:
            what_type = type(y).__name__
            flag = eval(what_type+"_nodeCheck(x, y)")
        else:
            flag = paramID_func(x, y)

        x = pattern_node.right
        y = file_node.right
        if flag and type(x).__name__ == type(y).__name__:
            what_type = type(y).__name__
            flag = eval(what_type+"_nodeCheck(x, y)")
        else:
            flag = paramID_func(x, y)

    return flag

def Break_nodeCheck(pattern_node, file_node):
    return True

def Cast_nodeCheck(pattern_node, file_node):
    flag = True
    x=pattern_node.to_type
    y=file_node.to_type
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y:
        flag = eval(type_y+'_nodeCheck(x,y)')
    else:
        flag = False

    x=pattern_node.expr
    y=file_node.expr
    type_x, type_y = type(x).__name__, type(y).__name__
    if flag and type_x == type_y:
        flag = eval(type_y+'_nodeCheck(x,y)')
    elif flag:
        flag = paramID_func(x, y)
    return flag

def Compound_nodeCheck(pattern_node, file_node):
    return True

def CompoundLiteral_nodeCheck(pattern_node, file_node):
    return True

def Constant_nodeCheck(pattern_node, file_node):
    paramID_func(pattern_node, file_node)
    return True

def Continue_nodeCheck(pattern_node, file_node):
    return True

def Decl_nodeCheck(pattern_node, file_node):
    flag = True
    # name attribute
    flag = paramID_func(pattern_node, file_node.name)
    #quals attribute
    for q in file_node.quals:
        IdentifierStore.append(q)
    # type attribute
    x,y = pattern_node.type, file_node.type
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y:
        flag = eval(type_y+'_nodeCheck(x,y)')
    elif type_y in ['PtrDecl', 'IdentifierType', 'ArrayDecl']:
        flag = eval(type_y+'_nodeCheck(x,y)')
    else:
        flag=False

    # the attribute storage and quals, I dont have much idea what they are doing right now
    # therefore to be added later maybe
    x, y= pattern_node.init, file_node.init
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x==type_y and flag:
        if type_x!='NoneType':
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            ## store the parameter when the init is None
            flag = paramID_func(pattern_node, file_node.name)
    elif type_x=='ID' and type_y=='Constant':
        flag = eval(type_y+'_nodeCheck(x,y)')
    else:
        flag=False

    return flag

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
            if type(x).__name__ == type(y).__name__ and flag:
                what_type = type(y).__name__
                flag = eval(what_type+"_nodeCheck(x, y)")
            else:
                flag = paramID_func(x, y)
    except:
        return False
    return True

def For_nodeCheck(pattern_node, file_node):
    return True

def FuncCall_nodeCheck(pattern_node, file_node):
    flag = ID_nodeCheck(pattern_node.name, file_node.name) and ExprList_nodeCheck(pattern_node.args, file_node.args)
    return flag or paramID_func(pattern_node, file_node)

def FuncDecl_nodeCheck(pattern_node, file_node):
    return True

def Goto_nodeCheck(pattern_node, file_node):
    return True

def ID_nodeCheck(pattern_node, file_node):
    if pattern_node.name == file_node.name:
        return True
    else:
        return paramID_func(pattern_node,file_node)

def IdentifierType_nodeCheck(pattern_node, file_node):
    identifier_store_func(pattern_node, file_node)
    return True

def If_nodeCheck(pattern_node, file_node):
    return True

def InitList_nodeCheck(pattern_node, file_node):
    return True

def Label_nodeCheck(pattern_node, file_node):
    return True

def NameInitializer_nodeCheck(pattern_node, file_node):
    return True

def ParamList_nodeCheck(pattern_node, file_node):
    return True

times=0
def PtrDecl_nodeCheck(pattern_node, file_node):
    ## again no code for quals
    global times
    times+=1
    flag = True
    y = file_node.type
    type_y =type(y).__name__
    if type(pattern_node).__name__=='PtrDecl':
        x = pattern_node.type
        type_x = type(x).__name__
        flag = eval(type_y+'_nodeCheck(x,y)')
    else:
        ptr_store(y,times)
        flag = eval(type_y+'_nodeCheck(pattern_node,y)')
    times-=1
    ## case when ptr to ptr
    #print(IdentifierStore)
    #if times==0 and len(IdentifierStore)>1 and isinstance(IdentifierStore[-2],list):
    #    del IdentifierStore[-1]
    return flag

def Return_nodeCheck(pattern_node, file_node):
    return True

def Struct_nodeCheck(pattern_node, file_node):
    return True

def StructRef_nodeCheck(pattern_node, file_node):
    return True

def Switch_nodeCheck(pattern_node, file_node):
    return True

def TernaryOp_nodeCheck(pattern_node, file_node):
    return True

def TypeDecl_nodeCheck(pattern_node, file_node):
    flag = False
    # other parameters I currently not aware of so not implementing
    x = pattern_node.type
    y = file_node.type
    if type(x).__name__ == type(y).__name__:
        what_type = type(x).__name__
        flag = eval(what_type+"_nodeCheck(x, y)")
    return flag

def Typedef_nodeCheck(pattern_node, file_node):
    return True

def Typename_nodeCheck(pattern_node, file_node):
    flag = False
    # other parameters I currently not aware of so not implementing
    x = pattern_node.type
    y = file_node.type
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y or type_y=='PtrDecl':
        flag = eval(type_y+"_nodeCheck(x, y)")
    return flag

def UnaryOp_nodeCheck(pattern_node, file_node):
    flag = False
    if pattern_node.op == file_node.op:
        x = pattern_node.expr
        y = file_node.expr
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x, y)
    return flag

def Union_nodeCheck(pattern_node, file_node):
    return True

def While_nodeCheck(pattern_node, file_node):
    return True

def Pragma_nodeCheck(pattern_node, file_node):
    return True

#####################################################################################################
## class iterators which find the required class range in initialPattern file
def pattern_iterator(node):
    what_type, start_line, end_line = getLineRange(node)
    f=open(file_initialPattern,'r')
    f.seek(start_line)
    offset=0
    changeMade = False
    line='initialSet'
    while offset <= end_line - start_line and line:
        line = f.readline()
        offset+=len(line)
        try:
            #extract the pattern
            if 'start:' in line.strip():
                pattern_string='int f(){\n'
                while True:
                    line = f.readline()
                    if 'end:' in line:
                        break
                    else:
                        pattern_string+=line
                    offset+=len(line)
                pattern_string+='}'
                #for debugging uncomment the following two lines
                #print(node.coord)
                #print(pattern_string)
                pattern_ast = build_pattern_AST(pattern_string)
                #travel down to the compound element
                pattern_ast = pattern_ast.ext[0].children()[1][1].children()
                flag = eval(what_type+"_nodeCheck(pattern_ast[0][1], node)")
                if flag:
                    changeMade = True
                    print('param: ',ParamStore)
                    print('iden: ',IdentifierStore)
                    print('assign: ',OpStore)
                    #print(node.coord.line, node.coord.column)
                    """
                    fd = open(file_dataStore,'a')
                    fd.write(str(ParamStore)+'\n')
                    fd.close()
                    """
            ParamStore[:]=[]
            IdentifierStore[:]=[]
            OpStore[:]=[]
        except:
            pass

    return changeMade
    f.close()

#####################################################################################################
def dfs_node_iterate(node):
    for xname, x in node.children():
        what_type = type(x).__name__
        changeMade = False
        #print(what_type)
        if what_type in classMap:
            #invoke the respective type check function
            changeMade = pattern_iterator(x)
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
