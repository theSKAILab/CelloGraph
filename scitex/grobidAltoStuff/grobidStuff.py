import xml.etree.ElementTree as ET


#this is the list of a bunch of spacing characters that show up in the xml that I don't want to include when doing string processing.
formatList = ['\n', '\t']

#just gets the div object cuz there's some junk to cut through first.
def findDiv(filepath):
    tree = ET.parse(filepath)
    
    root = tree.getroot() 
    text = root[2]
    body = text[0]

    return body


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
def stringBreaker(longstr):
    retval = []
    words = []
    bookmark = 0
    dividers = [' ']
    inTag = False
    for c in range(len(longstr)):
        testChar = chr(longstr[c])
        if testChar == '>':
            inTag = False
            bookmark = c+1
        elif not inTag and testChar == ' ' or (testChar == '<' and chr(longstr[c-1]) != '>' and chr(longstr[c-1]) not in formatList):
            if('4' == longstr[bookmark:c].decode()):
                print("break")
            
            retval.append([bookmark, c])
            words.append(longstr[bookmark:c].decode())


            bookmark = c+1
        if testChar == '<':
            inTag = True
    return retval


def stringFixer(supers, subs, map, longstr):
    tags = assembleTags(supers, subs, map)
    

    for i in range(len(tags)):
        tagDex, type = tags[i]
        start = tagDex[0]
        end = tagDex[1]

        text = longstr[start:end].decode()

        longstr = longstr[:start] + bytes("<", "utf-8") + bytes(type, "utf-8") + bytes(">", "utf-8") + longstr[start:end] + bytes("</", "utf-8") + bytes(type, "utf-8") + bytes(">", "utf-8") + longstr[end:]
        tagDex, type = tags[len(tags)-1]
    return longstr


#use the map for the tags so that 
def assembleTags(supers, subs, map):
    retval = []
    while(len(supers)!=0 or len(subs)!=0):
        dex, type = lastAmong(supers, subs)
        retval.append([map[dex], type])
        if type == "sub":
            subs.pop(len(subs)-1)
        if type == "super":
            supers.pop(len(supers)-1)
    return retval





def strWords(filepath):
    tree = ET.parse(filepath)
    longstr = ET.tostring(tree.getroot())
    
    retval = []
    bookmark = 0
    dividers = [' ']
    inTag = False

    

    for c in range(len(longstr)):
        testChar = chr(longstr[c])
        if testChar == '>':
            inTag = False
            bookmark = c+1
        elif not inTag and testChar == ' ' or (testChar == '<' and chr(longstr[c-1]) != '>' and chr(longstr[c-1]) not in formatList):
            
            #put the word into the list of words
            #yes I have to do it like this if I typecast as a string it adds b' to the beginning of every string
            #I don't know why and just increasing the index deletes from the word instead of the deleting the b'
            wordArr = [*longstr[bookmark:c]]
            word = ""
            for x in range(len(wordArr)):
                word += chr(wordArr[x])
                if(chr(wordArr[x]) in formatList):
                    word = "\\"
                    break
            if word != "\\":
                retval.append(word)
                bookmark = c+1
        if testChar == '<':
            inTag = True
    return retval


def longStr(filepath):
    tree = ET.parse(filepath)
    return ET.tostring(tree.getroot())


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

#filepath to the GROBID XML file
#supers is a list of indices that have superscript
#subs is the same but for subscript
#returns a remade BODY XML element with all script tags added.

#could this be broken into multiple functions? maybe, but the majority of it is a 4d loop
def addScript(filepath, supers, subs):

    supers.sort()
    subs.sort()

    body = findDiv(filepath)

    dex = 0
    targetDex, type = newTarget(supers, subs)
    

    for divDex in range(len(body)):
        div = body[divDex]
        if(len(div) >0):
            header = div[0]
            if(header.text):
                dex += len(header.text.split(' '))
                for paraDex in range(len(div[1:])):
                    para = div[paraDex]
                    sentDex = -1
                    while sentDex < len(para)-1:
                        sentDex += 1
                        sent = body[divDex][paraDex][sentDex]

                        if(sent.text):
                            sentCount = len(sent.text.split(' '))
                            if(dex + sentCount > targetDex and targetDex>0):
                                body[divDex][paraDex][sentDex] = injectScript(sent, targetDex-dex, type)
                                if(type == 'supers'):
                                    supers.pop(0)
                                elif(type == 'subs'):
                                    subs.pop(0)
                                targetDex, type = newTarget(supers, subs)
                                sentDex -= 1
                                continue
                            else:
                                dex += sentCount

                        #if there are citations breaking up the sentence, add those
                        if(len(body[divDex][paraDex][sentDex])>0):
                            citeDex = -1
                            while citeDex < len(body[divDex][paraDex][sentDex])-1:
                                citeDex += 1
                                cite = body[divDex][paraDex][sentDex][citeDex]
                                if(cite.text):
                                    dex += len(cite.text.split(' '))
                                if(cite.tail):
                                    sentCount = len(cite.tail.split(' '))
                                    if(dex + sentCount > targetDex and targetDex>0):
                                        #sentLen = len(sent)
                                        #bodyLen = len(body[i][j][k])
                                        #sentKids, bodyKids = [], []
                                        #for z in sent:
                                        #    sentKids.append(z)
                                        #for y in body[i][j][k]:
                                        #    bodyKids.append(y)
                                        body[divDex][paraDex][sentDex][citeDex] = injectScript(sent[citeDex], targetDex-dex, type, "tail")
                                        
                                        if(type == 'supers'):
                                            supers.pop(0)
                                        elif(type == 'subs'):
                                            subs.pop(0)
                                        targetDex, type = newTarget(supers, subs)
                                        citeDex -= 1
                                        continue
                                    else:
                                        dex += len(cite.tail.split(' '))

    return body


#def rebuild(filepath, body):
#    tree = ET.parse(filepath)
#    root = tree.getroot()
#
#    root[2].remove(root[2][0])
#    ET.SubElement(root[2], "body")
#    root[2][0] = body
#
#    newTree = ET.ElementTree(root)
#    
#    newTree.write(filepath + "scitex.xml")
#
#    return tree

def rebuild(filepath, longstr, supers, subs):

    longstr = stringFixer(supers, subs, stringBreaker(longstr), longstr)

    output = open("HeinzeSciTex5.xml", "w")
    output.write(longstr.decode())
    output.close()

    return longstr



#sent is the sentence the script is being injected into
#index is where the script is. This will be an int for one word or an array for a string
#type will be "super" or "sub" respectively.

#returns a sentence tag that should be exactly the same except the script tag has been added.

def injectScript(sent, index, type, mode="text"):
    if(index < 0):
        return sent

    if(mode == "text"):
        text = sent.text.split(' ')
    else:
        text = sent.tail.split(' ')
    

    retval = ET.Element('s')
    retval.text = ' '.join(text[:index])

    script = ET.SubElement(retval, type)
    script.text = text[index]

    if(index < len(text)-1):
        script.tail = ' '.join(text[index+1:])

    for ele in sent:
        newEle = ET.SubElement(retval, ele.tag)
        newEle = ele
        for sub in ele:
            newSubEle = ET.SubElement(newEle, sub.tag)
            newSubEle = sub

    return retval


def newTarget(supers, subs):
    if(len(supers) == 0 and len(subs) == 0):
        return -1, "neither"
    if(len(supers) == 0):
        return subs[0][0], "subs"
    if(len(subs) == 0):
        return supers[0][0], "supers"

    if(supers[0] > subs[0]):
        return subs[0][0], "subs"
    else:
        return supers[0][0], "supers"


def manualSplit(text):
    retval = []

    bookmark = 0
    for i in range(len(text)):
        if(text[i] == ' '):
            retval.append(text[bookmark:i])
            bookmark = i+1

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
                    for sent in para:
                        #add sentence text
                        if(sent.text):
                            retval += manualSplit(sent.text)

                        #if there are citations breaking up the sentence, add those
                        if(len(sent)>0):
                            for cite in sent:
                                retval += manualSplit(cite.text)
                                if(cite.tail):
                                    retval += manualSplit(cite.tail)
    
    retval = clean(retval)
    return retval


#returns the ith word.
#def grobidDex(filepath, i):


grobidWords("scitex/grobidAltoStuff/HeinzeGrobid.xml")


#go through page by page and remove page headers as you find them