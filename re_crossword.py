#pip install sre_yield


import sre_yield 
import string
import operator
import sys


solutions = []
isOk=False


#Replaces the toBeReplacePointer-th letter of Subject word with the characterToBePlaced
def stringReplace(subject, toBeReplacePointer, characterToBePlaced):
    list1 = list(subject)
    list1[toBeReplacePointer] = characterToBePlaced
    newString = ''.join(list1)
    return newString 


'''
Data Structures

dict for string : pattern
    number: The number assocciated with the word on the crossword
    text: The word to be find
    pattern: The regex corresponding to the text
    candidates: The candidate words fitting to the text
    candidatesNumber: The number of unique candidates
    common_cells: Pairs of words having common cells as a four element dict:
        the number of the first word as first_number
        the number of cell concerning thw first word first_position
        the number of the second word as second_number
        the number of cell concerning thw first word second_position

list of dicts
    all dicts that are assocciated with words are placed in a list
    
'''


'''
Reads two files and returns
a dict representing the unsolved crossword
a list containing the regular expresion
'''
def readFiles(csv, txt):
    #Opening and reading the two input files
    _csv = open(csv, 'r')
    csvLines = _csv.readlines()
    _txt = open(txt, 'r')
    txtLines = _txt.readlines()
    #array for getting the words derived from the first file
    CROSSWORD = []
    #array for getting the regex derived from the second file
    REGEXPRS  = []
    #Placing the regexs into the corresponding array
    for reg in txtLines:
        REGEXPRS.append(reg.rstrip())
    #constructing dict for each word and placing into the list
    for line in csvLines:
        #splitting thw line to comma
        parameters = line.split(",")
        #creating the dict
        word = dict()
        #inserting values into the dict
        word['text']=parameters[1]
        word['pattern']=""#pattern is initially empty
        word['number']=int(parameters[0])
        #this is the array containing the common cells with other words
        ccs = []
        #reading the pairs corresponding to the common cells
        for i in range(2,len(parameters)-1,2):
            #creating the dict for keeping the common cells with other words
            cc = dict()
            #the current word pair (number and position)
            cc['first_number']=int(parameters[0])
            cc['first_position']=-1    #initially the position is unknown   
            #the other word pair (number and position)
            cc['second_number']=int(parameters[i])
            cc['second_position']=int(parameters[i+1].rstrip())
            ccs.append(cc)
        word['common_cells'] = ccs
        CROSSWORD.append(word)
    return [CROSSWORD,REGEXPRS]

'''
Check common cells
'''
def MakeCommonCels(W):
    #examining all pairs of words (two for loops)
    for w in range(0,len(W)):
        for j in range(w+1,len(W)):
            #examing all pairs of common cell dicts (two for loops)
            for c in W[w]['common_cells']:
                for d in W[j]['common_cells']:
                    if j!=w:
                        #checking the pair having to do with their common cell
                        if  d['second_number']==c['first_number'] and c['second_number']==d['first_number'] and c['first_number']==W[w]['number'] and d['first_number']==W[j]['number']:
                            #updating the first_position element to each dict
                            c['first_position']=d['second_position']
                            d['first_position']=c['second_position']


'''
Creates a list with candidates words to be fitted to each word of thw W list.
Candidates are being constructed dependin on R list of regexs
after indicates the first W list element that is going to be examined 
'''
def FindCandidates(W, R, after = 0):
    candidates0 = []
    #CREATES CANDIDATE WORDS DEPENDING ON R
    #FOR EACH REGEX
    for c in R:
        #FOR EACH LENGTH
        for t in range(1,6):
            #CREATES CORRESPONDING LIST
            current_cand_list = sre_yield.AllStrings(c, max_count=t, charset=string.ascii_uppercase)
            #CONVERT IT TO PYTHON LIST
            CL = list(current_cand_list)
            #FOR EACH LIST ELEMENT
            for _cl in CL:
                #ADD IT TO CANDIDATES
                candidates0.append((_cl,c))
    #REMOVE DOUBLICATES
    candidates0 = list(dict.fromkeys(candidates0))
    #FOR EACH WORD
    for i in range(after, len(W)):
        w = W[i]
        #THE CANDIDATES LIST FOR THE WORD IS EMPTY
        candidatesLen = []
        #FOR EACH CANDIDATE
        for element in candidates0:
            #IF IT IS OF THE SAME LENGTH WITH THE WORD KEEP IT
            if len(element[0])==len(w['text']):
                candidatesLen.append(element)
        #FOR EACH CANDIDATE CHECKING IF IT IS OK WITH THE ALLREADY KNOWN LETTERS
        candidates = []
        #FOR EACH CHOSEN CANDIDATE
        for cnd in candidatesLen:
            ok = 1
            #FOR EACH LETTER OF THE CURRENT WORD
            for j in range(0,len(w['text'])):
                #IF THE LETTER IS NOT . AND IS DIFFERENT THAN THE CANDIDATE (SAME POSITION)
                if w['text'][j]!='.' and w['text'][j]!=cnd[0][j]:
                    ok = 0#DO NOT KEEP IT 
                    break;
            if ok == 1:
                candidates.append(cnd)
        #REMOVE DOUBLICATES
        candidates = list(dict.fromkeys(candidates))
        #Updating word dict data
        w['candidates'] = candidates
        w['candidatesNumber']=len(candidates)
        



def ConstructCrossWord(csv,txt):
    #reading crossword elements from file and constructing the crossword elements
    cw, re = readFiles(csv, txt)
    #computing the common cells
    MakeCommonCels(cw)
    #computing the candidate words
    FindCandidates(cw, re)
    #sorting word dicts by the candatesNumber element
    cw.sort(key=operator.itemgetter('candidatesNumber'))
    return [cw,re]




'''
checks if the crossword is solved
'''
def AllWordsCompleted(c):
    #if a word containing . exists then the crossword is not solved
    for w in c:
        for i in range(0,len(w['text'])):
            if w['text'][i] == '.':
                return False
    return True



'''
computes cadidates for each word into the c list depending on expr list
starting fro thw after-th element
'''
def CandidatesComputation(c, expr, after = 0):
        w = c[after]
        #updating the common words after the current word
        for i in range(after+1,len(c)):
            nxtw = c[i]
            for common in w['common_cells']:
                if common['second_number'] == nxtw['number']:
                    nxtw['text'] = stringReplace( nxtw['text'], common['second_position'], w['text'][common['first_position']])
        #recomputing candidates
        FindCandidates(c, expr, after+1)        





def rearrangingList(c, after):
    _list = []
    _new_list=[]
    for i in range(after, len(c)):
        _list.append(c[i])
    _list.sort(key=operator.itemgetter('candidatesNumber'))
    for i in range(0,after):
        _new_list.append(c[i])
    for i in range(0, len(_list)):
        _new_list.append(_list[i])
    return _new_list


'''
Solves the crossword
'''
def Solve(c,w, r, allSols = False):
    global isOk      #flag for indicating that the crossword solved
    global solutions #list containing solutions found
    if isOk == False:#if not solved
        if w == len(c):#if reaching the last word in the list
            if AllWordsCompleted(c):#if all words found
                isOk = True #flag --> Solved
                solutions.append(c) ##append the solution to the list
        else:
            if len(c[w]['candidates'])>0: #if candidate word exist
                for i in c[w]['candidates']: #for each candidate
                    if isOk == True and allSols==False: #if solved and we need only one solution stop
                        break
                    if  i[1] in r: #for each regex
                       
                        _c = c.copy() #make a copy of words list
                        _r = r.copy() #make a copy of regex list
                        _w = w+1      #move to the next word pointer in list
                        
                        _c[w]['text'] = i[0]    #the current word text = the candidate word
                        _c[w]['pattern'] = i[1] #update the pattern used
                        _r.remove(i[1])         #remove the pattern used from available
                        
                        CandidatesComputation(_c, _r, w)  #update the candidate words for the rest words
                        _c = rearrangingList(_c, _w)      #rearraging the list of words depending the new candidates (as the number of candidates for each word has been changed)
                        Solve(_c,_w,_r)                   #keep solving 





#geting the solutions from c list
def exportSolution(c, allSols = False):
    if len(c)==0:
        print("There is no solution")
    else:
        #print only the first solution
        if allSols == False:
            c[0].sort(key=operator.itemgetter('number'))
            for e in c[0]:
                print(str(e['number'])+". "+e['text']+" "+e['pattern'])
        else:
            #print all solutions
            for _c in c:
                _c.sort(key=operator.itemgetter('number'))
                print("Solution----------------------------------------")
                for e in _c:
                    
                    print(str(e['number'])+". "+e['text']+" "+e['pattern'])
                print("-----------------------------------------------")





def main(argv):
    if len(sys.argv)==3:
        try:
            cw, re = ConstructCrossWord(sys.argv[1],sys.argv[2])
            try:
                #solve recursivelly the crossword
                Solve(cw,0,re,True)
                try:
                    exportSolution(solutions, False)
                except:
                    print("Error exporting the solution");
            except:
                print("Error solving crossword")
        except:
            print("Error while constructing the crossword structure")
    else:
        print("Check Command Systax")
        print("python re_crossword.py crossword_file regular_expressions_file")
    
if __name__ == "__main__":
   main(sys.argv[1:])


