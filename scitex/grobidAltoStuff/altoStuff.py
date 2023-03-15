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
        

#if the word's font is on the list of fonts, then return True
def isScript(word, supers, subs):
    word_id = word.get("STYLEREFS")
    for font in supers:
        font_id = font.get("ID")
        if(word_id == font_id):
            return "super"
    for font in subs:
        if(word_id == font_id):
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
        if(style):
            if("superscript" in style):
                subFonts.append(font)
            elif("subscript" in style):
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
        stringList.append(word.get("CONTENT"))
    
    stringList = clean(stringList)
    return stringList, wordList, superFonts, subFonts

