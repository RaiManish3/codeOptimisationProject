import re
from os.path import expanduser
home = expanduser("~")

file_in = home+"/.vscode/extensions/codeOptimisationProject/req/doASTreplace/output.txt"
file_out = home+"/.vscode/extensions/codeOptimisationProject/req/printString/updateOut.txt"

with open(file_in, 'r') as fs, open(file_out, 'w') as fd:
	strx=''
	for line in fs:
		if re.match(r'^\d+,\d+,\d+,\d+', line) != None:
			strx+=line
	fd.write(strx)
