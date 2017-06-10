# from start line and col do the following
# char that need to have a count -> ", { , (
import linecache

#file_in = "../sample_c_programs/sample.c"
#fout = 'trial.txt'

def getCol(file_in, line1, col1, line2, col2):
    lst=[]
    quoteC, hasBrace, gotIt = 1, False, False
    nquote, nbrace, nparen = 0, 0, 0
    while True:
        line = linecache.getline(file_in, line1)
        i=0
        for ch in line:
            i+=1
            if ch=='\"':
                nquote+= quoteC
                quoteC*=-1
            elif ch=="{":
                hasBrace = True
                nbrace+=1
            elif ch=="}":
                nbrace-=1
                if hasBrace and hbrace==0:
                    lst.append((line1, i+1))
                    gotIt=True
                    break
            elif ch=="(":
                nparen+=1
            elif ch==")":
                nparen-=1
            elif ch==';':
                if nquote==0 and nparen==0 and nbrace==0 and line>=line2 and i>=col2:
                    ## we have the end point
                    lst.append((line1, i+1))
                    gotIt=True
                    break
        if gotIt:
            break
        line1+=1

    return lst[0]
