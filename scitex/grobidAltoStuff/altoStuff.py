import xml.etree.ElementTree as ET
import difflib as dl


def clean(textArr):
    if(len(textArr) == 0):
        return textArr
    i = -1
    while i < len(textArr)-1:
        i += 1
        if(textArr[i] == ''):
            textArr.pop(i)
            i -= 1
    return textArr
        
def pullFromContext_Diff(gen):
    list1 = []
    list2 = []

    inList1 = False
    for diff in gen:
        if(diff[1] == ' ' and len(list1) == 0):
            inList1 = True
            list1.append(diff)
        elif(diff[1] == ' ' and inList1):
            list1.append(diff)
        elif(diff[1] != " " and inList1):
            inList1 = False
        elif(diff[1] == ' ' and not inList1):
            list2.append(diff)

    return list1, list2


def lcs(S,T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])

    return lcs_set

def get_len_long_substr(str1, str2):
    substring = []
    len_str1 = len(str1)
    len_str2 = len(str2)
    dexes = [0, 0]
    length = 0

    if len_str1 > 0:
        for i in range(len_str1):
            for j in range(len_str1 - i + 1):
                for k in range(len_str2):
                    if(j>length and str1[i:i+j] == str2[k:k+j]):
                        for m in str1[i:i+j]:
                            if m[0] != ' ':
                                bad = True
                                break
                        if(bad):
                            continue
                        else:
                            substring = str1[i:i+j]
                            dexes = [i, k]
                            length = j

    return dexes[0], dexes[1], length, substring


def lcs(S,T):
    S1 = tuple(S)
    T1 = tuple(T)
    m = len(S1)
    n = len(T1)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    longestDex = [0, 0]
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            sW = S1[i]
            tW = T1[j]
            if S1[i] == T1[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest and c>1:
                    lcs_set = set()
                    longest = c
                    longestDex = [i-c+1, j-c+1]
                    lcs_set.add(S1[i-c+1:i+1])
                    str1 = S[i-c+1:i+1]
                elif c == longest:
                    lcs_set.add(S1[i-c+1:i+1])

    
    return longestDex[0], longestDex[1]

def sync(groStrings, altStrings, aD=0, gD=0, checkSize=20):
    retval = lcs(groStrings[gD:gD+checkSize], altStrings[aD:aD+checkSize])
    if(retval != [0, 0]):
        return retval
    else:
        return sync(groStrings, altStrings, aD, gD, 400)



#    for i in range(len(altStrings)-aD):
#        altW = altStrings[i+aD:i+5+aD]
#        for j in range(checkSize):
#            groW = groStrings[j+gD:j+5+gD]
#            if(altStrings[i+aD:i+5+aD] == groStrings[j+gD:j+5+gD]):
#                alt = altStrings[i+aD:i+5+aD]
#                if("P-CH" in alt):
#                    print("break")
#                gro = groStrings[j+gD:j+5+gD]
#                return i+aD, j+gD
#    if(aD + i < len(altStrings)-1):
#        return sync(groStrings, altStrings, aD, gD, len(groStrings))
#    else:
#        return aD+1, gD+1

#if the word's font is on the list of fonts, then return True
def isScript(word, supers, subs):
    id = word.get("STYLEREFS")
    for font in supers:
        if(id == font.get("ID")):
            return "super"
    for font in subs:
        if(id == font.get("ID")):
            return "sub"
    return False

#takes a filepath to a pdfalto XML file
#returns stringList, wordList, fontList
#stringList is an array of strings
#wordList is an array of alto words
#fontList is an array of the fonts that are super or subscript in that document.
def AltoLists(filepath):
    tree = ET.parse(filepath)
    
    wordList = []    
    stringList = []
    subFonts = []
    superFonts = []

    root = tree.getroot() 
    
    layout = root[2]
    page = layout[0]
    printedSpace = page[0]

    styles = root[1]
    for font in styles:
        style = font.get("FONTSTYLE")
        if(style == "superscript"):
            subFonts.append(font)
        elif(style == "subscript"):
            superFonts.append(font)

    for page in layout:
        for space in page:
            for block in space:
                for line in block:
                    for string in line:
                        #elements of lines will either be words or spaces, 
                        # words will have a CONTENT string.
                        if(string.get("CONTENT")):
                            wordList.append(string)
    
    for word in wordList:
        stringList.append(word.get("CONTENT").encode())
    
    stringList = clean(stringList)
    return stringList, wordList, superFonts, subFonts

