import xml.etree.ElementTree as ET
import io
import copy


#this is the list of a bunch of spacing characters that show up in the xml that I don't want to include when doing string processing.
formatList = ['\n', '\t']
whiteSpace = ['', b'', '\n', b'\n']

#just gets the div object cuz there's some junk to cut through first.
# filepath: String filepath
# returns: ElementTree.Element which contains the main text.
def findBody(filepath):

    with io.open(filepath, "rb") as f:
        root = ET.parse(f).getroot()

    list = []
    for thing in root:
        list.append(thing)
    
    text = root.find("{http://www.tei-c.org/ns/1.0}text")

    return text.find("{http://www.tei-c.org/ns/1.0}body")

#removes empty strings from a list of strings.
# textArr: List of strings
# returns: List of strings
def clean(textArr):

    whiteSpaceCount = 0

    if(len(textArr) == 0):
        return textArr
    i = -1
    while i < len(textArr)-1:
        i += 1
        if(textArr[i] in whiteSpace):
            textArr.pop(i)
            i -= 1
            whiteSpaceCount += 1
        elif(textArr[i] == b'.' or textArr[i] == '.'):
            textArr[i-1] += '.'
            textArr.pop(i)
            i -= 1
        else:
            if isinstance(textArr[i], bytes):
                textArr[i] = textArr[i].decode()
    return textArr



#accepts a long string, designed to return a list of indices for where each individual word is.    
# longstr: String version of the grobid XML.
# returns: List of shape [[int, int], ...] where retval[0] is the first and last character of the first word.
def stringBreaker(longstr, mode="map"):
    retval = []
    words = []
    bookmark = 0
    inTag = False

    c = -1
    while c < len(longstr) -1:
        c += 1
        testChar = chr(longstr[c])
        if testChar == '>':
            inTag = False
            bookmark = c+1
        elif bookmark != c and not inTag and testChar == ' ' or (testChar == '<' and chr(longstr[c-1]) != '>' and chr(longstr[c-1]) not in formatList):            
            ret = [bookmark, c]
            word = longstr[bookmark:c].decode()
            add = True

            if(word == '' or word == ' '):
                add = False
            elif(word[0] == ' '):
                ret[0] += 1
                word = word[1:]
            elif(word[len(word)-1] == ' '):
                ret[1] -= 1
                word = word[:len(word)-1]
            elif(word == '.'):
                words[len(words)-1] += '.'
                add = False
            

            if(add):
                retval.append(ret)
                words.append(word)
            bookmark = c+1

        if testChar == '<':
            inTag = True

    if(mode=="words"):
        return words
    return retval


#finds the number of words before the main text so it can be used as an offset.
# filepath: String filepath of the grobid output
# returns: int, the number of words present before the main text.
def findBodyOffSet(filepath):
    with io.open(filepath, "rb") as f:
        root = ET.parse(f).getroot()

    #need the len of root[0] and root[1]

    textDex = 0

    #find the text thing
    for c in range(len(root)):
        if(root[c].tag == "{http://www.tei-c.org/ns/1.0}text"):
            textDex = c

    words = []
    #get the size of the things before it.
    for i in range(textDex):
        stringi = ET.tostring(root[i])
        wordsi = stringBreaker(stringi)
        for j in range(len(wordsi)):
            words.append(stringi.decode()[wordsi[j][0]:wordsi[j][1]])
        words.append(len(wordsi))

    cleaned = clean(words)
    wordOff = len(cleaned)

    return wordOff - textDex

def findFigOffset(filepath):
    bodyOff = findBodyOffSet(filepath)

    bodyWords = grobidBodyWords(filepath)
    bodyLen = len(bodyWords)
    
    return bodyOff + bodyLen


#puts all the script tags in.
# filepath: String
# supers: List of shape [[int, bytestring], ...] of which words need to be surrounded by superscript tags.
# subs: List of shape [[int, bytestring], ...] of which words need to be surrounded by subscript tags.
# map: List of shape [[int, int], ...] where map[0] is the first word, and contains the index of its first and last character.
# returns: String, which can be turned into an XML file.
def stringFixer(filepath, supers, subs, map):

    bodySupers, figSupers = supers[0], supers[1]
    bodySubs, figSubs = subs[0], subs[1]

    wordOffset = findBodyOffSet(filepath)

    tags = assembleTags(bodySupers, bodySubs, map, wordOffset)

    figOffset = findFigOffset(filepath)

    tags = assembleTags(figSupers, figSubs, map, figOffset) + tags

    longstr = longStr(filepath)

    for i in range(len(tags)):
        tagDex, type = tags[i]
        start = tagDex[0] 
        end = tagDex[1]
        
        longstr = longstr[:start] + bytes("<", "utf-8") + bytes(type, "utf-8") + bytes(">", "utf-8") + longstr[start:end] + bytes("</", "utf-8") + bytes(type, "utf-8") + bytes(">", "utf-8") + longstr[end:]
        tagDex, type = tags[len(tags)-1]  
    
    return longstr


# supers: list of shape [[int, bytestring], ...] where int is the index of a superscript word.
# subs: list of shape [[int, bytestring], ...] where int is the index of a subscript word.
# map: list of shape [[int, int], ...] where map[0] is the first and last character of the first word.
# offset: an offset to be applied to the map.
def assembleTags(supers, subs, map, offset):

    retval = []
    while(len(supers)!=0 or len(subs)!=0):
        dex, type = lastAmong(supers, subs)
        retval.append([map[dex+offset], type])
        if type == "sub":
            subs.pop(len(subs)-1)
        if type == "super":
            supers.pop(len(supers)-1)
    return retval


# ET.tostring() with extra steps.
# filepath: String filepath of the grobid output.
# returns: String representation of the XML but with all irregular characters formatted properly.
def longStr(filepath):

    tree = ET.parse(filepath)
    
    longString = ET.tostring(tree.getroot())

    #wordsString = grobidWords(filepath, "str")

    c = -1
    decimal_marker = -1
    hex_marker = -1

    while c < len(longString)-1:
        c += 1

        if hex_marker > 0 and (chr(longString[c] == ' ')):
            num = int(longString[hex_marker+2:c])
            longString = longString[:hex_marker] + longString[hex_marker+2:c].decode() + longString[c:]
            hex_marker = -1

        #if there's a character that's being stupid and was replaced with a Unicode encoding number
        if(longString[c:c+2] == b"&#"):
            decimal_marker = c

        if(longString[c:c+2] == b"\\x"):
            hex_marker = c

        if decimal_marker > 0 and (chr(longString[c]) == ';'):

            num = int(longString[decimal_marker+2:c])

            #replace it with the right character. 
            #Yes I have to decode and then re-encode it that is unfortunately how chr() works.
            

            if(True):
                longString = longString[:decimal_marker] + chr(int(longString[decimal_marker+2:c].decode())).encode() + longString[c+1:]
            #else:
                #call 'fixFunkyPDFChars' from old Scitex.
            decimal_marker = -1

        

    
    return longString

# returns the index and type of whichever script tag is last in the document.
# supers: list of shape [[int, bytestring], ...] of all superscript tags
# subs: list of shape [[int, bytestring], ...] of all subscript tags.
# returns: int, string where int is the index of the tag and string is "sub", "super", or "neither"
def lastAmong(supers, subs):
    if(len(subs) == 0 and len(supers) == 0):
        return -1, 'neither'
    if(len(subs)>0):
        lastSub = subs[len(subs)-1][0]
    else:
        lastSub = -1

    if(len(supers)>0):
        lastSuper = supers[len(supers)-1][0]
    else:
        lastSuper = -1

    if(lastSub > lastSuper):
        return lastSub, 'sub'
    else:
        return lastSuper, 'super'


# adds the script tags and writes out the output.
# sourcePath: String, filepath to the grobid output
# outputName: String, name of the output file.
# supers: list of shape [[int, bytestring], ...] where int is the location of superscript words.
# subs: list of shape [[int, bytestring], ...] where int is the location of subscript words.
# returns: String, the contents of the XML
def rebuild(sourcePath, outputName, supers, subs):
    longstr = longStr(sourcePath)

    longstr = stringFixer(sourcePath, supers, subs, stringBreaker(longstr))

    with io.open(outputName,'w',encoding='utf8') as f:
        f.write(longstr.decode())

    return longstr


#string.split(' ') with extra steps because we want them to be bytestrings.
# text: String text
# returns: list of shape [bytestring, ...] of the text, split by spaces.
def manualSplit(text):
    if not text:
        return None
    retval = []

    bookmark = 0
    for i in range(len(text)):
        if(text[i] == ' '):
            retval.append(text[bookmark:i].encode())
            bookmark = i+1
    retval.append(text[bookmark:].encode())

    i = -1
    while i < len(retval)-1:
        i += 1
        word = retval[i]
        if word == b'.' and i != 0:
            retval[i-1] += b'.'
            retval.pop(i)
            i -= 1


    return retval

#returns an array of all the words
def grobidBodyWords(filepath, output="arr"):
    
    body = findBody(filepath)
    divArr = body.findall("{http://www.tei-c.org/ns/1.0}div")
    retval = []

    for div in divArr:
        for child in div.iter():
            if(child.text):
                retval += manualSplit(child.text)
            if(child.tail):
                retval += manualSplit(child.tail)
                
    retval = clean(retval)

    if(output == "str"):
        return b' '.join(retval)

    return retval


def grobidFigWords(filepath):
    body = findBody(filepath)

    figureArr = body.findall("{http://www.tei-c.org/ns/1.0}figure")

    retval = []
    
    for figure in figureArr:
        for thing in figure.iter():
            if(thing.text):
                retval += manualSplit(thing.text)
            if(thing.tail):
                retval += manualSplit(thing.tail)
        
    retval = clean(retval)
    return retval
