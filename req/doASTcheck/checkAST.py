#-----------------------------------------------------------------
# pycparser: checkAST.py
#
# Using pycparser scanning C file, looking for sensitive patterns
# and storing their information in a file.
#
# Manish Rai
#-----------------------------------------------------------------
from __future__ import print_function
import os
import sys
import itertools
import re
from os.path import expanduser
home = expanduser("~")

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
sys.path.extend(['.', '..'])

from pycparser import c_parser, c_ast, parse_file, c_generator
import getRange

##definitions
INF = float("inf")
ZERO = 0
line1, col1, line2, col2 = INF, INF, ZERO, ZERO

##globals
#dictionary mapping class types to line range in initialPattern file
classMap = {'Assignment':(2,10), 'Decl':(12,17),'FuncCall':(19, 21),'If':(23,25)}
c_file = ''
file_initialPattern = home+"/.vscode/extensions/codeOptimisationProject/req/doASTcheck/initialPattern.txt"
file_dataStore = home+"/.vscode/extensions/codeOptimisationProject/req/doASTcheck/data.txt"
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

def write_to_file(rl1,rl2):
    fd = open(file_dataStore,'a')
    fd.write(str(ParamStore)+"\n")
    fd.write(str(IdentifierStore)+"\n")
    fd.write(rl1+","+rl2+"\n")
    fd.write(str(line1)+","+str(col1)+","+str(line2)+","+str(col2)+ '\n')
    fd.close()

def deleteContent():
    with open(file_dataStore, "w"):
        pass

def generatorC(file_node):
    generator = c_generator.CGenerator()
    try:
        return generator.visit(file_node)
    except:
        return file_node

def updateCoord(node):
    global line1, col1, line2, col2
    try:
        line = node.coord.line
        if line ==0:
            return
        col = node.coord.column
        if line<=line1:
            if line<line1:
                line1=line
                if col is not None:
                    col1 = col
            if col is not None and col<col1:
                col1=col
        if line>=line2:
            if line>line2:
                line2=line
                if col is not None:
                    col2 = col
            if col is not None and col>col2:
                col2=col
    except:
        pass

"""
## try using regex
reg_spl = ['.','?','\\','(',')','!','$','^','*','+','{','}','[',']','#','=','<','>']
def getCoord(file_node, start_line=1):
    file_string = generatorC(file_node)
    ## iterate
    fx = open(c_file, 'r')
    strx = ' '
    flag = True
    print(file_string)
    for i in file_string:
        if i==' ':
            if flag:
                if not (len(strx)>=3 and strx[-3:]=='\s*'):
                    strx+='\s*'
                flag = False
        elif i in reg_spl:
            strx+='\\'+i+'\s*'
            flag = True
        else:
            strx+=i
            flag = True
        print(strx , i)
#---------------------------------
    try:
        fx = open(c_file, 'r')
        all_lines = ''.join(fx.readlines())
        file_string = re.sub(r'\\\s+','\\s*',file_string)
        print(all_lines)
        if file_string[-3:] =='\s*':
            file_string = file_string[:-3]

        print(file_string)
        matching = re.search(file_string, all_lines)
        print(matching)
        #matching = re.search(file_string, all_lines).group(0)
        #print(matching)
        #print(len(matching.splitlines()[-1]))
        #fx.close()
    except:
        print("error")

"""

def getLineRange(node):
    ## gives the start and end line for the required class
    ## in initialPattern file
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
        ParamStore.append(generatorC(file_node))

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
    updateCoord(file_node)
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
    return flag

def ArrayRef_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
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
    updateCoord(file_node)
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
    updateCoord(file_node)
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
    updateCoord(file_node)
    #not a threat
    return True

def Case_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    #to be decided
    return True

def Cast_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
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
    updateCoord(file_node)
    ## what to do with compound element
    ## decide in a discussion
    flag = False
    if type(pattern_node).__name__ == 'Compound':
        x,y= pattern_node.block_items,file_node.block_items
        if len(x)> len(y):
            return False
        tmp = zip(x,y)
        for x, y in tmp:
            flag = eval(type(y).__name__+'_nodeCheck(x,y)')
            if not flag:
                break
    else:
        flag = paramID_func(pattern_node, file_node)
    return flag

def CompoundLiteral_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Constant_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## the type of the constant is also important
    ParamStore.append([file_node.type, file_node.value])
    return True

def Continue_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    #not a threat
    return True

def Decl_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
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
    updateCoord(file_node)
    flag=False
    try:
        x, y = pattern_node.decls, file_node.decls
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x==type_y and len(x)==len(y):
            tmp = zip(x,y)
            for xx, yy in tmp:
                type_yy = type(yy).__name__
                flag = eval(type_yy+'_nodeCheck(xx,yy)')
                if not flag:
                    break
        else:
            flag = paramID_func(x,y)
    except:
        flag = paramID_func(pattern_node, file_node)
    return flag

def Default_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def DoWhile_nodeCheck(pattern_node, file_node):
    ## similar to While so forwarding this case to that of While
    return While_nodeCheck(pattern_node,file_node)

def EllipsisParam_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def EmptyStatement_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Enum_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## precoded so it wont alter the execution of program
    return True

def Enumerator_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## name: value pairs for enum
    ## precoded so it wont alter the execution of program
    return True

def EnumeratorList_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## list for enum
    return True

def ExprList_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = True
    try:
        if len(pattern_node.exprs)> len(file_node.exprs):
            return False
        tmp = zip(pattern_node.exprs,file_node.exprs)
        for x, y in tmp:
            if type(x).__name__ == type(y).__name__ and flag:
                what_type = type(y).__name__
                flag = eval(what_type+"_nodeCheck(x, y)")
            else:
                flag = paramID_func(x, y)
    except:
        return False
    return True

def For_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## the implementation :: when the parameters are when defined
    ## the evaluation is strict checking for each construct
    flag = False
    ##init attribute : in most cases we would like to store it
    try:
        x,y = pattern_node.init,file_node.init
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)

        if not flag: return False
        ##cond attribute : in most cases we would like to store it
        x,y = pattern_node.cond,file_node.cond
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)

        if not flag: return False
        ##next attribute : in most cases we would like to store it
        x,y = pattern_node.next,file_node.next
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)

        if not flag: return False
        ##stmt attribute : in most cases we would like to store it
        x,y = pattern_node.stmt,file_node.stmt
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)
    except:
        flag = False
    return flag

def FuncCall_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = ID_nodeCheck(pattern_node.name, file_node.name) and ExprList_nodeCheck(pattern_node.args, file_node.args)
    return flag or paramID_func(pattern_node, file_node)

def FuncDecl_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Goto_nodeCheck(pattern_node, file_node):
    return True

def ID_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    if pattern_node.name == file_node.name:
        return True
    else:
        return paramID_func(pattern_node,file_node)

def IdentifierType_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    identifier_store_func(pattern_node, file_node)
    return True

def If_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = False
    ##init attribute : in most cases we would like to store it
    try:
        x,y = pattern_node.cond,file_node.cond
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)

        if not flag: return flag
        x,y = pattern_node.iftrue,file_node.iftrue
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)

        if not flag: return flag
        x,y = pattern_node.iffalse,file_node.iffalse
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            if type_y!='NoneType':
                flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x,y)
    except:
        flag = False
    return flag

def InitList_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Label_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def NameInitializer_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def ParamList_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

times=0
def PtrDecl_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
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
    return flag

def Return_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Struct_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def StructRef_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def Switch_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def TernaryOp_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def TypeDecl_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = False
    # other parameters I currently not aware of so not implementing
    x,y = pattern_node.type,file_node.type
    if type(x).__name__ == type(y).__name__:
        what_type = type(x).__name__
        flag = eval(what_type+"_nodeCheck(x, y)")
    return flag

def Typedef_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## not a threat
    return True

def Typename_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = False
    # other parameters I currently not aware of so not implementing
    x,y = pattern_node.type,file_node.type
    type_x, type_y = type(x).__name__, type(y).__name__
    if type_x == type_y or type_y=='PtrDecl':
        flag = eval(type_y+"_nodeCheck(x, y)")
    return flag

def UnaryOp_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = False
    try:
        if pattern_node.op == file_node.op:
            x,y = pattern_node.expr,file_node.expr
            type_x, type_y = type(x).__name__, type(y).__name__
            if type_x == type_y:
                flag = eval(type_y+'_nodeCheck(x,y)')
            else:
                flag = paramID_func(x, y)
    except:
        flag = paramID_func(pattern_node, file_node)
    return flag

def Union_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    return True

def While_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    flag = False
    try:
        ## the cond must be either equal or x must have param set to its name
        y,x = file_node.cond, pattern_node.cond
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x, y)

        ## the stmts that follow must be either equal or x must have param set to its name
        y,x = file_node.stmt, pattern_node.stmt
        type_x, type_y = type(x).__name__, type(y).__name__
        if type_x == type_y:
            flag = eval(type_y+'_nodeCheck(x,y)')
        else:
            flag = paramID_func(x, y)
    except:
        # the case when pattern_node does not have the similar structure as file_node or lacks param fields
        flag = False
    return flag

def Pragma_nodeCheck(pattern_node, file_node):
    updateCoord(file_node)
    ## not a threat
    return True

#####################################################################################################
## class iterators which find the required class range in initialPattern file
def pattern_iterator(node,filename):
    global line1, col1, line2, col2
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
                rl1,rl2 = line.strip().split(':')[1:]
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
                #print(pattern_string)
                pattern_ast = build_pattern_AST(pattern_string)
                #travel down to the compound element
                pattern_ast = pattern_ast.ext[0].children()[1][1].children()
                flag = eval(what_type+"_nodeCheck(pattern_ast[0][1], node)")
                if flag:
                    changeMade = True
                    #debugging print statements
                    """
                    print('param: ',ParamStore)
                    print('iden: ',IdentifierStore)
                    print('assign: ',OpStore)
                    print(line1,col1,line2,col2)
                    """
		    line2, col2 = getRange.getCol(filename, line1,col1, line2, col2)
                    write_to_file(rl1,rl2)
            ParamStore[:]=[]
            IdentifierStore[:]=[]
            OpStore[:]=[]
            line1,col1,line2,col2=INF,INF,ZERO,ZERO
        except:
            pass

    return changeMade
    f.close()

#####################################################################################################
def dfs_node_iterate(node, filename):
    for xname, x in node.children():
        what_type = type(x).__name__
        changeMade = False
        #print(what_type)
        if what_type in classMap:
            #invoke the respective type check function
            changeMade = pattern_iterator(x, filename)
        #Do not iterate again on parts whose children had the changes
        if not changeMade:
            dfs_node_iterate(x,filename)

#generate the AST for the C program and does a DFS on it
def check(filename):
    ast = parse_file(filename, use_cpp=True)
    dfs_node_iterate(ast,filename)                               # implement dfs here


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
        c_file = sys.argv[1]
    else:
        c_file = home+'.vscode/extensions/codeOptimisationProject/req/sample_c_files/sample.c'

    loadfileOptimised()
    deleteContent()
    check(c_file)
