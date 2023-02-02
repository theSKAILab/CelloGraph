import xml.etree.ElementTree as ET

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


def rebuild(filepath, body):
    tree = ET.parse(filepath)
    root = tree.getroot()

    root[2].remove(root[2][0])
    ET.SubElement(root[2], "body")
    root[2][0] = body

    newTree = ET.ElementTree(root)
    
    newTree.write(filepath + "scitex.xml")

    return tree





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


#returns an array of all the words
def grobidWords(filepath, output="arr"):
    
    body = findDiv(filepath)
    retval = []
    
    for header in body:
        if('div' in header.tag):
            head = header[0]
            if(head.text):
                retval += head.text.split(' ')
                for para in header[1:]:
                    for sent in para:
                        #add sentence text
                        if(sent.text):
                            retval += sent.text.split(' ')

                        #if there are citations breaking up the sentence, add those
                        if(len(sent)>0):
                            for cite in sent:
                                retval += cite.text.split(' ')
                                if(cite.tail):
                                    retval += cite.tail.split(' ')
    
    retval = clean(retval)
    return retval


#returns the ith word.
#def grobidDex(filepath, i):


grobidWords("scitex/grobidAltoStuff/HeinzeGrobid.xml")


#go through page by page and remove page headers as you find them