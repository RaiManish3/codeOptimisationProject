from pycparser import c_parser, c_ast, parse_file, c_generator
import linecache
from itertools import islice

dicto = {}
## file to be read or written
function = 'replacementPattern.txt'
out_file = 'output.txt'
dfile = '../doASTcheck/data.txt'
cou = 0


def changeIdentifierChar(node, lst):	#change identifier type
	for xname, x in node.children():
		if type(x).__name__ == 'IdentifierType':
			x.names[0] = lst[int(cou)]
		changeIdentifierChar(x, lst)


def changeIdentifierInt(node, lst):	#change identifier type
	for xname, x in node.children():
		if type(x).__name__ == 'IdentifierType':
			x.names[0] = lst[int(cou)+1]
		changeIdentifierInt(x, lst)


def addPointer(node, val):		#adds the pointer as per the value of val
	ori = node
	val = int(val)
	for i in xrange(val):
		ori.type = c_ast.PtrDecl([],None)
		ori = ori.type
	return ori


def delPointer(node):			#delete instances of PteDecl
	x = node.type
	y = node.type
	if type(x).__name__ == 'PtrDecl':
		y = delPointer(x)
	return y


def pointerAssign(ast, ide, nod):		#main PtrDecl handlin function
	global cou
	if type(ast).__name__ != 'PtrDecl':
		nod = ast
	for xname, x in ast.children():
		if type(x).__name__ == 'TypeDecl':
			try:
				if type(ide[cou]).__name__ == 'int':
					upw = addPointer(nod, ide[cou])
					changeIdentifierInt(x, ide)
					upw.type = x
					cou = cou + 2
				else:
					changeIdentifierChar(x, ide)
					nod.type = x
					cou = cou + 1
			except IndexError:
				return
		else:
			pointerAssign(x, ide, nod)



def printChange(node, lno):		# prints the final output in a list
	sta = int(lno[0])
	end = int(lno[2])
	ran = end - sta + 1
	lst = []
	generator = c_generator.CGenerator()
	stri = generator.visit(node)
	stri = stri[13:-3].strip()
	return stri


def replacVar(ast, par):		#replaces variable with the values given
	for xname, x in ast.children():
		try:
			if x.name.startswith('param'):
				ind = int(x.name[5:])
				val = par[ind]
				x.name = val
			replacVar(x, par)
		except AttributeError:
			try:
				if x.declname.startswith('param'):
					ind = int(x.declname[5:])
					val = par[ind]
					x.declname = val
				replacVar(x, par)
			except AttributeError:
				replacVar(x, par)



def getFunc(lno):			#generates ast for the replacement function
	sta = lno[0]
	end = lno[2]
	lst = []
	for i in range(eval('int(sta)'), eval('int(end)+1')):
		line = (linecache.getline(function, i)).strip()
		lst.append(line)
	stri = ''
	for l in lst:
		stri = stri + l
	stri = 'func(){' + stri + '}'
        parser = c_parser.CParser()
	ast = parser.parse(stri)
	return ast


def extract(lines):			#extract the information from the set of four lines
	global cou
	if lines == [] or lines == ['\n']:
		return
	para = lines[0].strip()
	par = eval(para)
	idee = lines[1].strip()
	ide = eval(idee)
	lno = lines[2].strip()
	coo = lines[3].strip()
	cou = 0
	ast = getFunc(lno)
	bst = ast.ext[0].body
	replacVar(ast, par)
	if ide!=[]:
		pointerAssign(bst, ide, ast)
	out = printChange(ast, lno)
	stri = str(coo) + '\n' + str(out) + '\n'
	temp = open(out_file,'a')
	temp.write(stri)
	temp.close()


if __name__ == '__main__':
	with open(out_file , 'w'):
		pass
	with open(dfile) as f:
		while True:
			lines = list(islice(f, 4))
			extract(lines)
			if not lines:
				break
