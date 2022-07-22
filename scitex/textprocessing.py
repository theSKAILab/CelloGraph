import spacy
from spacy.matcher import Matcher
import re
import copy
import PDFfragments
import minorfunctions
import time


# takes an array of things, takes all the text out, then puts it all into one string.
# has two modes: dictionary mode and class mode. Dictionary mode will use the "text" item from the dictionary.
# Class mode will use the "text" field


def makeString(arr, mode="dict"):
    retval = ""
    if(mode == "dict"):
        for item in arr:
            retval += item["text"]
            retval += " "
    if(mode == "class"):
        for item in arr:
            retval += item.text
            retval += " "
    return retval


#
def MakeSentences(words, coords, p, pagenum, colnum, pdfSettings=None):
    retval = []
    # set up some spacy stuff to detect end of sentence
    nlp = spacy.load("en_core_web_sm")
    sentMatcher = Matcher(nlp.vocab)
    sentPattern = [{"TEXT": "."}]
    qPattern = [{"TEXT": "?"}]
    ePattern = [{"TEXT": "!"}]
    bracketclosePattern = [{"SHAPE": "]."}]
    bracketopenPattern = [{"SHAPE": ".["}]
    numPattern = [{"SHAPE": "ddd-dddd).[dd"}]
    citePattern = [{"ORTH": "]"}, {"ORTH": "}"}]

    sentMatcher.add("Sentences", [sentPattern,
                    qPattern, ePattern, bracketclosePattern, bracketopenPattern, numPattern, citePattern])

    sentNum = 0
    bookmark = 0
    text = ""

    for i in range(len(words)):
        str = makeString([words[i]])
        doc = nlp(str)
        matches = sentMatcher(doc)

        # for each sentence, add it to the list and then move the bookmark forward
        for id, start, end in matches:

            # don't add the sentence if it's inside parenthesis/brackets or there's no whitespace after
            paren = False
            dots = True
            sent = False
            text = nlp(makeString(words[bookmark:i+1]))
            
            for t in range(len(text) - 1, -1, -1):

                char = text[t].text
                if char != '.':
                    dots = False
                else:
                    sent = True
                if(char == "al" and sent and t == len(text)-2):
                    sent = False
                    break
                if char == ')' or char == ']':
                    break
                if char == '(' or char == '[':
                    paren = True
                    break
                if(len(text) > 4):
                    test = text[len(text)-2:].text
                    if(text[len(text)-4:].text == "etc." or text[len(text)-4:].text == "et."):
                        break

            if(sent and not dots and not paren):
                retval.append(PDFfragments.sentence(
                    words[bookmark:i+1], text.text, coords, p, sentNum, [pagenum, colnum], [pagenum, colnum]))
                sentNum += 1
                text = ""
                bookmark = i+1

    # if it somehow didn't catch something then add that something to the end
    if(bookmark != len(words)):
        retval.append(PDFfragments.sentence(
            words[bookmark:], makeString(words[bookmark:]), coords, p, sentNum, [pagenum, colnum], [pagenum, colnum]))
        word = words[len(words)-1]
        finalchar = word["chars"][len(word["chars"])-1]["text"]
        if(pdfSettings and pagenum > 2 and finalchar != ']' and finalchar != ' ' and finalchar != '.'):
            pdfSettings.addtoNext = True

    if(pdfSettings):
        return pdfSettings, retval
    return retval


def stitchSentences(sentences):
    sentDex = -1
    while sentDex < len(sentences)-2:
        sentDex += 1
        sentence = sentences[sentDex]
        if(not sentence):
            sentences.pop(sentDex)
            sentDex -= 1
            continue
        index = 1
        char = sentence.text[len(sentence.text)-index]
        while(index < len(sentence.text) and char == ' '):
            index += 1
            char = sentence.text[len(sentence.text)-index]
        if(char != '.' and char != '!' and char != '?'):
            sentences[sentDex] += sentences[sentDex+1]
            sentences.pop(sentDex+1)
    return sentences


# gets rid of any super or subscript at the end of the word so you can look at just the base word.
def trimScript(str):
    i = -1
    while i < len(str)-1:
        i += 1
        if(str[i] == '_' or str[i]==' '):
            str = str[:i] + str[i+1:len(str)]
    return str


def checkForCutOffs(sentences):
    if(len(sentences) == 0):
        return sentences

    for i in range(len(sentences)):
        j = 0
        while(j < len(sentences[i].text)-3):
            text = sentences[i].text
            j += 1
            if(text[j:j+2] == '- ' and text[j-1] != ' '):
                sentences[i].text = sentences[i].text[:j] + \
                    sentences[i].text[j+2:]
                j -= 2

    return sentences


# this is a function to facilitate a very complicated if statement.
def DetermineParagraph(lines, lineIndex, pdfSettings, error):
    w = lines[lineIndex]["LineStartDex"]
    words = lines[lineIndex]["Words"]
    if(w == pdfSettings.bookmark):
        return False
    if(not pdfSettings.useSpace):
        if(lineIndex < len(lines)-1):
            currentAlign = minorfunctions.areEqual(
                lines[lineIndex]["Align"], pdfSettings.paraAlign, error)
            nextAlign = minorfunctions.areEqual(
                lines[lineIndex+1]["Align"], lines[lineIndex]["Align"], error)
            return not currentAlign and not nextAlign
        else:
            return True
    else:
        if(w < len(words)-1):
            return minorfunctions.isGreater(
                words[w]["top"] - words[w+1]["top"], pdfSettings.paraSpace, error)
        else:
            return False


# returns true if w is the first word on a new line.
def newline(words, w, error=0):
    if(w == 0):
        return True
    # if(words[w][top] <= words[w-1][top] or words[w][bottom] >= words[w-1][bottom]):
    #    return False
    # else:
    #    return True
    height = words[w]["bottom"] - words[w]["top"]
    topGreater = not minorfunctions.isLesser(
        words[w]["top"], words[w-1]["top"], height/2)
    bottomLesser = not minorfunctions.isGreater(
        words[w]["bottom"], words[w-1]["bottom"], height/2)
    newCol = minorfunctions.isLesser(
        words[w]["top"]-words[w-1]["top"], 0, height/4)
    if(topGreater and bottomLesser and not newCol):
        return False
    return True


def newCell(words, w, vError, hError):
    prevtop = words[w-1]["top"]
    top = words[w]["top"]
    prevX = words[w-1]["x1"]
    X = words[w]["x0"]
    height = words[w]["bottom"] - words[w]["top"]
    width = float(words[w]["x1"] - words[w]["x0"])

    # if new col
    if(minorfunctions.isGreater(X, prevX, width+hError)):
        return True

    if(minorfunctions.isGreater(top, prevtop, float(height)*2.1) and minorfunctions.isLesser(X, prevX)):
        return True

    return False


def newRow(words, w, vError, hError):
    prevtop = words[w-1]["top"]
    top = words[w]["top"]
    prevX = words[w-1]["x1"]
    X = words[w]["x0"]
    height = words[w]["bottom"] - words[w]["top"]
    width = float(words[w]["x1"] - words[w]["x0"])

    # if new row
    if(minorfunctions.isGreater(top, prevtop, float(height)*2.1) and minorfunctions.isLesser(X, prevX)):
        return True
    return False




# if the page number is either the first word, or
# is tacked onto the beginning of the first word, remove it.
def removePageNumber(words, num):
    original = words
    words = removePageNumberWord(words, num)
    size = words[300:]
    if(words != original):
        return words
    words = removePageNumberFromBeginningOfWord(words, num)
    return words



#remove the page number from the front of words if it's a word in the array
# words is an array of word dictionaries (see PDFfunctions.makeWord or comments at the bottom of PDFfragments.py)
# num is an integer, it's the page number.
def removePageNumberWord(words, num):
    size = words[300:]
    if(len(words) < 1):
        return words
    if(words[0]["text"] == str(num)):
        words = words[1:]
        return words
    if(words[len(words)-1]["text"] == str(num)):
        words = words[:len(words)-1]
        return words
    return words



#remove the page number if it's at the beginning of the first word of the array.
# words is an array of word dictionaries (see PDFfunctions.makeWord or comments at the bottom of PDFfragments.py)
# num is an integer, it's the page number.
def removePageNumberFromBeginningOfWord(words, num):
    if(len(words) < 1):
        return words
    if(words[0]["text"][0:len(str(num))] == str(num)):
        words[0]["text"] = words[0]["text"][len(str(num)):]
    return words



def FindsectionType(sectionheader, active, pagenum=1, height=4, error=0):
    retval = 0
    if(isinstance(sectionheader, str)):
        for i in range(len(sectionheader)):
            if(sectionheader[i] == '.'):
                if(i > 0 and sectionheader[i-1].isdigit()):
                    retval += 1
            if(sectionheader[len(sectionheader)-1].isdigit()):
                retval += 1
    else:
        height = sectionheader["bottom"] - sectionheader["top"]
        for i in range(len(sectionheader["text"])):
            if(sectionheader["text"][i] == '.'):
                if(i > 0 and sectionheader["text"][i-1].isdigit()):
                    retval += 1
        if(sectionheader["text"][len(sectionheader["text"])-1].isdigit()):
            retval += 1

    if(pagenum == 1 or active.pagenum == 1):
        if(retval == 0):
            return 1
        return retval
    else:
        test = active
        while(test):
            if(minorfunctions.areEqual(height, test.height, error)):
                if(retval != 0):
                    return retval
                else:
                    return test.type
            elif(minorfunctions.isGreater(height, test.height, error)):
                if(retval == test.type-1 or retval == 1):
                    return retval
                else:
                    test = test.parent
            elif(minorfunctions.isLesser(height, test.height, error)):
                if(retval >= test.type+1):
                    return retval
                else:
                    retval += 1

        if(retval != 0):
            return retval
        else:
            return test.type



#I'm not sure I actually use this anywhere.
def isValid(str):
    for i in str:
        if not i.isdigit():
            return True
    return False



#NOTE: THIS FUNCTION DOESN'T ACTUALLY GET USED ANYWHERE YET
# Searches the page for citations and removes them.
# returns a string with all citations removed.
def CitationRemoval(cites, PDF, word, coords, paraNum):
    # find all the citations
    pattern = r'\[\i\]'
    results = re.finditer(pattern, word["text"])

    # add each one to the PDF's list of citations and then remove it.
    for match in results:
        newcite = PDFfragments.citation(
            word["text"][match.start(): match.end()], copy.copy(coords), paraNum)
        cites.append(newcite)
        pattern = re.compile(pattern)
        word["text"] = pattern.sub('', word["text"])
    return word




# returns a 2d array of word dictionaries, organized into their respective columns.
# words is an array of word dictionaries, hError and vError are integers
def HandleColumns(words, hError, vError):
    sec1 = time.time()
    retval = [[]]
    c = 0

    for w in range(len(words)):
        #get some variables
        prevtop = words[w-1]["top"]
        top = words[w]["top"]
        prevX = words[w-1]["x1"]
        X = words[w]["x0"]

        # if it's on a new line but that new line is higher on the page and further to the right, make a new column.
        if(newline(words, w, vError) and minorfunctions.isLesser(top, prevtop, vError) and minorfunctions.isGreater(X, prevX, hError)):
            c += 1

        # add a new array to the 2d array if we need to, in order to put words there.
        while(c > (len(retval) - 1)):
            retval.append([])

        retval[c].append(words[w])

    sec2 = time.time()
    print("Seconds to Handle Columns: " + str(sec2 - sec1))
    return retval



#takes and returns sentlist (an array of sentence objects) and pdfSettings (see PDFsettings.py)
def cleanPara(sentlist, pdfSettings):
    #if we don't actually have any sentences, return
    if(len(sentlist) == 0):
        return sentlist, pdfSettings

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentlist[0].text)
    if(len(doc) > 0):
        if(doc[0].is_lower or doc[0].is_punct):
            pdfSettings.addto = True

    i = -1
    while i < len(sentlist)-1:
        i += 1
        doc = nlp(sentlist[i].text)
        if(len(doc) > 0):
            if(doc[0].is_lower and i != 0):
                sentlist[i-1].text += " " + sentlist[i].text
                sentlist.pop(i)
                i -= 1
            elif(len(sentlist[i].text) < 10):
                if(i == 0 and len(sentlist) > 1):
                    sentlist[i+1].text = sentlist[i].text + \
                        " " + sentlist[i+1].text
                    sentlist.pop(i)
                    i -= 1
                    # add it to the next sentence
                elif(i != 0):
                    sentlist[i-1].text += " " + sentlist[i].text
                    sentlist.pop(i)
                    i -= 1

    return sentlist, pdfSettings
