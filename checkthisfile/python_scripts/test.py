import random
inputFile = 'python_scripts/testing/check1.txt'
f = open(inputFile,'w')
strx=''
for i in xrange(5):
    strx+=str(random.randint(1,9))+","+str(random.randint(1,9))+","+str(random.randint(1,9))+","+str(random.randint(1,9))+"\n"
f.write(strx)
f.close()
