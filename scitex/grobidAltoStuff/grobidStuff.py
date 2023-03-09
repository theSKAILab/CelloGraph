import xml.etree.ElementTree as ET
import io
import copy

#this is the list of a bunch of spacing characters that show up in the xml that I don't want to include when doing string processing.
formatList = ['\n', '\t']

#just gets the div object cuz there's some junk to cut through first.
# filepath: String filepath
# returns: ElementTree.Element which contains the main text.
def findDiv(filepath):

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
    if(len(textArr) == 0):
        return textArr
    i = -1
    while i < len(textArr)-1:
        i += 1
        if(textArr[i] == ''):
            textArr.pop(i)
            i -= 1
    return textArr



#accepts a long string, designed to return a list of indices for where each individual word is.    
# longstr: String version of the grobid XML.
# returns: List of shape [[int, int], ...] where retval[0] is the first and last character of the first word.
def stringBreaker(longstr):
    retval = []
    words = []
    bookmark = 0
    inTag = False

    for c in range(len(longstr)):
        testChar = chr(longstr[c])
        if testChar == '>':
            inTag = False
            bookmark = c+1
        elif not inTag and testChar == ' ' or (testChar == '<' and chr(longstr[c-1]) != '>' and chr(longstr[c-1]) not in formatList):            
            retval.append([bookmark, c])
            words.append(longstr[bookmark:c].decode())
            bookmark = c+1
        if testChar == '<':
            inTag = True
    return retval


#finds the number of words before the main text so it can be used as an offset.
# filepath: String filepath of the grobid output
# returns: int, the number of words present before the main text.
def findDivOffSet(filepath):
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

    wordOff = len(words)

    return wordOff - textDex


#puts all the script tags in.
# filepath: String
# supers: List of shape [[int, bytestring], ...] of which words need to be surrounded by superscript tags.
# subs: List of shape [[int, bytestring], ...] of which words need to be surrounded by subscript tags.
# map: List of shape [[int, int], ...] where map[0] is the first word, and contains the index of its first and last character.
# returns: String, which can be turned into an XML file.
def stringFixer(filepath, supers, subs, map):

    wordOffset = findDivOffSet(filepath)

    tags = assembleTags(supers, subs, map, wordOffset)

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

    while c < len(longString):
        c += 1

        #if there's a character that's being stupid and was replaced with a Unicode encoding number
        if(longString[c:c+2] == b"&#"):

            #replace it with the right character. 
            #Yes I have to decode and then re-encode it that is unfortunately how chr() works.

            longString = longString[:c] + chr(int(longString[c+2:c+5].decode())).encode() + longString[c+6:]

    
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
        f.write(longstr.decode(encoding="UTF-8"))

    return longstr


#string.split(' ') with extra steps because we want them to be bytestrings.
# text: String text
# returns: list of shape [bytestring, ...] of the text, split by spaces.
def manualSplit(text):
    retval = []

    bookmark = 0
    for i in range(len(text)):
        if(text[i] == ' '):
            retval.append(text[bookmark:i].encode())
            bookmark = i+1
    retval.append(text[bookmark:].encode())

    return retval

#returns an array of all the words
def grobidWords(filepath, output="arr"):
    
    body = findDiv(filepath)
    retval = []
    
    for header in body:
        if('div' in header.tag):
            head = header[0]
            if(head.text):
                retval += manualSplit(head.text)
                for para in header[1:]:
                    if(para.text):
                        retval += manualSplit(para.text)
                    if(para.tail):
                        retval += manualSplit(para.tail)
                    for sent in para:
                        #add sentence text
                        if(sent.text):
                            retval += manualSplit(sent.text)
                        if(sent.tail):
                            retval += manualSplit(sent.tail)

                        #if there are citations breaking up the sentence, add those
                        if(len(sent)>0):
                            for cite in sent:
                                retval += manualSplit(cite.text)
                                if(cite.tail):
                                    retval += manualSplit(cite.tail)
                        

    
    retval = clean(retval)

    if(output == "str"):
        return b' '.join(retval)

    return retval