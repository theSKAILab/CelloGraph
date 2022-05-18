import spacy
from spacy.matcher import Matcher
import re
import copy
import PDFfragments
import minorfunctions


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
def MakeSentences(str, coords, p):
    retval = []
    # set up some spacy stuff to detect end of sentence
    nlp = spacy.load("en_core_web_sm")
    sentMatcher = Matcher(nlp.vocab)
    sentPattern = [{"TEXT": "."}]
    qPattern = [{"TEXT": "?"}]
    ePattern = [{"TEXT": "!"}]
    bracketPattern = [{"SHAPE": "xxxx.[dd"}]
    numPattern = [{"SHAPE": "ddd-dddd).[dd"}]

    sentMatcher.add("Sentences", [sentPattern,
                    qPattern, ePattern, bracketPattern, numPattern])

    doc = nlp(str)
    bookmark = 0
    sentNum = 0
    matches = sentMatcher(doc)
    # for each sentence, add it to the list and then move the bookmark forward
    for id, start, end in matches:
        # if not match "(|[ x* .|?|! x* ]|)"
        paren = False
        for t in range(start, bookmark-1, -1):
            token = doc[t]
            if token.text == ")" or token.text == "]":
                break
            if token.text == "(" or token.text == "[":
                paren = True
                break

        if(paren == False):
            span = doc[bookmark: end]
            testthingy = doc[bookmark]
            bookmark = end
            retval.append(PDFfragments.sentence(span.text, coords, p, sentNum))
            sentNum += 1

    # if it somehow didn't catch something then add that something to the end
    if(bookmark != len(doc)):
        retval.append(PDFfragments.sentence(
            doc[bookmark:].text, coords, p, sentNum))
    return retval


# this is a function to facilitate very complicated if statements.
def DetermineParagraph(words, w, pdfSettings, error):
    if(not pdfSettings.useSpace):
        if(w < len(words)-1):
            retval = newline(words, w+1, error) and not minorfunctions.areEqual(
                words[w+1]["x0"], pdfSettings.paraAlign, error)
            return retval
        else:
            return True
    else:
        if(w < len(words)-1):
            return minorfunctions.isGreater(
                words[w]["top"] - words[w+1]["top"], pdfSettings.paraSpace, error)
        else:
            return False


def newline(words, w, error=0):
    if(w == 0):
        return True
    if(not minorfunctions.areEqual(words[w-1]["top"], words[w]["top"], error) and not minorfunctions.areEqual(
            words[w-1]["bottom"], words[w]["bottom"]), error):
        return True
    return False

# ratio is the height/space ratio of the current line
# lineratio is the expected ratio of a normal line
# same for height and lineheight
# diffs is the list of lines
# d is the current index in that list


def Determinesection(ratio, lineratio, height, lineheight, diffs, d, ratioerror):
    if(ratio < .3):
        return False
    # if we think this line is a section
    if(ratio < lineratio-ratioerror and height > lineheight):
        # if the next line is a section, or the line after is normal.
        if(d < len(diffs)-3 and diffs[d+2]["AftRatio"] > lineratio-ratioerror):
            return True
    return False


def FindsectionType(sectionheader):
    retval = 0
    if(isinstance(sectionheader, str)):
        for i in range(len(sectionheader)):
            if(sectionheader[i] == '.'):
                if(i > 0 and sectionheader[i-1].isdigit()):
                    retval += 1
            if(sectionheader[len(sectionheader)-1].isdigit()):
                retval += 1

    else:
        for i in range(len(sectionheader["text"])):
            if(sectionheader["text"][i] == '.'):
                if(i > 0 and sectionheader["text"][i-1].isdigit()):
                    retval += 1
        if(sectionheader["text"][len(sectionheader["text"])-1].isdigit()):
            retval += 1

    if(retval == 0):
        return 1
    return retval


# Searches the page for citations and removes them.
# returns a string with all citations removed.

def CitationRemoval(cites, PDF, word, coords, paraNum):
    # find all the citations
    pattern = r'\[\d\]'
    results = re.finditer(pattern, word["text"])

    # add each one to the PDF's list of citations and then remove it.
    for match in results:
        newcite = PDFfragments.citation(
            word["text"][match.start(): match.end()], copy.copy(coords), paraNum)
        cites.append(newcite)
        pattern = re.compile(pattern)
        word["text"] = pattern.sub('', word["text"])
    return word


def HandleColumns(words, hError, vError):
    retval = [[]]
    c = 0

    for w in range(0, len(words)):
        prevspace = words[w-1]["x1"] - words[w-2]["x0"]
        space = words[w]["x1"] - words[w-1]["x0"]
        if(minorfunctions.isGreater(space, prevspace, hError)) and minorfunctions.isGreater(
                words[w-1]["top"], words[w]["top"], vError):
            c += 1
        if(newline(words, w, vError)):
            c = 0
        while(c > (len(retval) - 1)):
            retval.append([])
        retval[c].append(words[w])
    return retval
