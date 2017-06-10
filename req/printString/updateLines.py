import re

file_in = "req/doASTreplace/output.txt"
file_out = "req/printString/updateOut.txt"

with open(file_in, 'r') as fs, open(file_out, 'w') as fd:
	strx=''
	for line in fs:
		if re.match(r'^\d+,\d+,\d+,\d+', line) != None:
			strx+=line
	fd.write(strx)
