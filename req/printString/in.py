import sys, re, linecache

output = 'req/doASTreplace/output.txt'




def colchange(clk):		# no. of lines same as before
	line = (lst[clk].split('\n')[0]).split(',')
	lth = len(lst[clk-1].split('\n')[0])
	for nu, lin in enumerate(lst):
		if re.match(r'^\d+,\d+,\d+,\d+', lin, re.M) != None:
			lin = (lin.split('\n')[0]).split(',')
			if nu == clk:
				if lin[0] == lin [2]:
					lin[3] = str(int(lin[1]) + lth)
				else:
					lin[3] = str(lth - 1)
				lin = ','.join(lin) + '\n'
				#print lst
			 	lst[nu] = lin
					
				
			if nu > clk:
				#print lin
				if line[0] == line[2] and lin[0] == line[0]:
					clinc = lth - (int(line[3])-int(line[1]))
					#print clinc
					if lin[0] == lin [2]:
						lin[3] = str(int(lin[3]) + clinc)
						lin[1] = str(int(lin[1]) + clinc)
					else:
						lin[1] = str(int(lin[1]) + clinc)
				else:
					if int(lin[0]) == int(line[2]):
						#print 'gh'
						clinc = lth - int(line[3])
						if lin[0] == lin [2]:
							lin[1] = str(int(lin[1]) + clinc)
							lin[3] = str(int(lin[3]) + clinc)
						else:
							lin[1] = str(int(lin[1]) + clinc)	
				lin = ','.join(lin) + '\n'
				#print lst
			 	lst[nu] = lin
	for i in range(prev+1, val+1):
		del lst[prev+1]
	stri = ''.join(lst)
	fd = open('samplenew.txt','w')
	fd.write(stri)
	fd.close()
	

def change(inc, clk):		#if number of lines later are more tha before
	stri = ''
	lth = len(lst[clk-1].split('\n')[0])
	line = (lst[clk].split('\n')[0]).split(',')
	#print line[2]
	#print lth
	for nu, lin in enumerate(lst):
		if re.match(r'^\d+,\d+,\d+,\d+', lin, re.M) != None:
			lin = (lin.split('\n')[0]).split(',')
			if nu == clk:
				lin[3] = str(lth - 1)
				lin[2] = str(int(lin[2])+inc)
				lin = ','.join(lin) + '\n'
				#print lst
			 	lst[nu] = lin			
			
			if nu > clk:
				#print lin[0]
				if line[2] == lin[0]:
					clinc = lth
					if lin[0] == lin [2]:
						lin[3] = str(int(lin[3]) + clinc - int(lin[1]))
						lin[1] = str(clinc)
					else:
						lin[1] = str(clinc)	
				lin[0] = str(int(lin[0]) + inc)
				lin[2] = str(int(lin[2]) + inc)	
				lin = ','.join(lin) + '\n'
				#print lst
			 	lst[nu] = lin
	for i in xrange(prev+1, val+1):
		del lst[prev+1]
	stri = ''.join(lst)
	fd = open(output,'w')
	fd.write(stri)
	fd.close()



def search(ln,cl):		#search for rrange
	global lst
	global prev
	prev = -1
	fd = open(output,'r')
	lst = fd.readlines()
	#print lst
	for nu, lin in enumerate(lst):
		#print lin
		if re.match(r'^\d+,\d+,\d+,\d+', lin, re.M) != None:
			lin = (lin.split('\n')[0]).split(',')
			#print lin
			if lin[0] == lin[2]:			
				if lin[0] == ln and int(lin[1]) <= int(cl) and int(lin[3]) >= int(cl):
					return nu
				else:
					prev = nu
			else:
				if lin[0] == ln and int(lin[1]) <= int(cl):
					return nu
				else:
					if lin[2] == ln and int(lin[3]) >= int(cl):
						return nu
					else:
						if int(lin[0]) < int(ln) and int(lin[2]) > int(ln):
							return nu
						else:
							prev = nu
		
	return None



if __name__ == '__main__':
	ln = sys.argv[1]
	cl = sys.argv[2]
	val = search(ln, cl)
	#print val		
	if val == None:
		assert False
	else:
		lin = ((lst[val]).split('\n')[0]).split(',')
		line = ''
		ori = int(lin[2]) - int(lin[0])+1
		for i in range(prev+1, val+1):
			line += lst[i] 
		print line
		qus = lst[val]
		if val - prev - 1 > ori:
			change(val-prev-1-ori, val)
		else:
			colchange(val)
		
		
		
	
