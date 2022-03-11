import spacy
from spacy.matcher import Matcher
import re
import copy
import PDFfragments

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
        span = doc[bookmark: end]
        bookmark = end
        retval.append(PDFfragments.sentence(span.text, coords, p, sentNum))
        sentNum += 1

    # if it somehow didn't catch something then add that something to the end
    if(bookmark != len(doc)):
        retval.append(PDFfragments.sentence(
            doc[bookmark:].text, coords, p, sentNum))
    return retval


# this is a function to facilitate very complicated if statements.
def DetermineParagraph(words, w, paraAlign, paraSpace, useSpace, error):
    if(not useSpace):
        if(w < len(words)-1):
            return words[w+1]["top"] != words[w]["top"] and int(words[w+1]["x0"]) != paraAlign
        else:
            return True
    else:
        if(w < len(words)-1):
            return float(words[w]["top"] - words[w+1]["top"]) + error > paraSpace
        else:
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
        if(d < len(diffs[0])-3 and diffs[2][d+2] > lineratio-ratioerror):
            return True
    return False

# Takes a "word" and determines what section depth it is.
# Don't have great terminology yet, but determines if its x. ; x.y. ; x.y.z. etc

# If the "word" isn't actually section coordinates then it returns as if x.


def FindsectionType(word):
    retval = 0
    for i in range(len(word["text"])):
        if(word["text"][i] == '.'):
            if(i > 0 and word["text"][i-1].isdigit()):
                retval += 1
    if(word["text"][len(word["text"])-1].isdigit()):
        retval += 1
    if(retval == 0):
        return 1
    return retval


# Searches the page for citations and removes them.
# returns a string with all citations removed.

def CitationRemoval(cites, PDF, word, coords, paraNum):
    # find all the citations
    pattern = r'\[+\d+\]'
    results = re.finditer(pattern, word["text"])

    # add each one to the PDF's list of citations and then remove it.
    for match in results:
        newcite = PDFfragments.citation(
            word["text"][match.start(): match.end()], copy.copy(coords), paraNum)
        cites.append(newcite)
        pattern = re.compile(pattern)
        word["text"] = pattern.sub('', word["text"])
    return word
