import spacy
from spacy.matcher import Matcher
import re
import textprocessing
import PDFfragments
import minorfunctions
import copy
import decimal


# look through each page header and if it matches the beginning of the page,
# remove the page header from the page.
# Also removes page numbers from the beginning of the page.
def removePageHeadersEarly(words, num, pdfSettings):
    words = textprocessing.removePageNumber(words, num)

    for i in range(len(pdfSettings.pageHeaders)):
        header = minorfunctions.reverseArr(
            pdfSettings.pageHeaders[i].text, "text")
        wordtext = minorfunctions.reverseArr(words, "text")
        if(minorfunctions.BeginningEqual(header, wordtext)):
            words = CutWords(words, pdfSettings.pageHeaders[i].text)
            if(pdfSettings.pageHeaders[i].expect_num):
                words = textprocessing.removePageNumber(words, num)
    if(words[0]["text"] == ""):
        words = words[1:]
    return words


def removePageFootersEarly(words, num, pdfSettings):
    words = textprocessing.removePageNumber(words, num)
    heck = words[300:]
    doubleheck = words[600:]

    for i in range(len(pdfSettings.pageFooters)):
        header = minorfunctions.reverseArr(
            pdfSettings.pageFooters[i].text, "text")
        wordtext = minorfunctions.reverseArr(words, "text")
        if(minorfunctions.EndEqual(header, wordtext)):
            words = CutWordsEnd(words, pdfSettings.pageFooters[i].text)
            if(pdfSettings.pageFooters[i].expect_num):
                words = textprocessing.removePageNumber(words, num)
    if(words[len(words)-1]["text"] == ""):
        words = words[:len(words)-1]
    return words

# takes words off of large as long as they match the words in small.


def CutWords(large, small):
    if(len(large) == 0 or len(small) == 0):
        return large
    if(len(large) < len(small)):
        return CutWords(small, large)
    for i in range(len(small)-1, -1, -1):
        if small[i]["text"] == large[i]["text"] or large[i]["text"] == "":
            large.pop(i)
        else:
            return large
    return large


def CutWordsEnd(large, small):
    if(len(large) == 0 or len(small) == 0):
        return large
    if(len(large) < len(small)):
        return CutWordsEnd(small, large)
    i = 0
    while i < len(small):
        i += 1
        if small[len(small)-i]["text"] != large[len(large)-i]["text"] and large[len(large)-i]["text"] != "":
            return large
    return large[:len(large)-i]


# removes any text that's between pdfplumber line objects.
def removeTables(PDF, page, words, error):
    objs = page.objects

    try:
        objs["line"]
    except:
        return PDF, words

    highestLine = minorfunctions.heighestLine(objs)
    lowestLine = minorfunctions.lowestLine(objs)

    retval = []
    currentRow = []
    remove = []

    for w in range(len(words)-1):
        if(textprocessing.newline(words, w+1, error)):
            if(len(currentRow) != 0):
                retval.append(currentRow)
                currentRow = []
        if minorfunctions.isGreater(words[w]["top"], highestLine["top"], error) and minorfunctions.isLesser(words[w]["bottom"], lowestLine["bottom"], error):
            currentRow.append(words[w])
            remove.append(w)

    if len(currentRow) != 0:
        retval.append(currentRow)

    PDF.tables.append(retval)

    for i in range(len(remove)-1, -1, -1):
        words.pop(remove[i])

    return PDF, words


# goes through all the words and organizesnlp them into diff objects
# diffs are essentially lines of text (maybe I should rename them...)
# they do have some accompanying stats like height and spacing for ease of access.
def getLines(words, pdfSettings, error):
    lines = []

    prevLineBegin = 0
    currentLineBegin = 0
    nextLineBegin = 0

    for w in range(len(words)-1):

        # if the first word is lowercase, then a paragraph probably got split up.
        if(w == 0):
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(words[0]["text"])
            if(len(doc) > 0):
                if(doc[0].is_lower):
                    pdfSettings.addto = True

        if(textprocessing.newline(words, w, error) and w != 0):

            if(nextLineBegin == 0):
                nextLineBegin = w
                continue

            lines, prevLineBegin, currentLineBegin, nextLineBegin = addLine(
                lines, words, prevLineBegin, currentLineBegin, nextLineBegin, w)

    # get the second to last line
    lines, prevLineBegin, currentLineBegin, nextLineBegin = addLine(
        lines, words, prevLineBegin, currentLineBegin, nextLineBegin, len(words)-1)

    # get the last line
    lines, prevLineBegin, currentLineBegin, nextLineBegin = addLine(
        lines, words, prevLineBegin, currentLineBegin, len(words), len(words)-1)

    # deal with Cutoffs
    words, lines = DealWithCutOffs(words, lines)

    return words, lines, pdfSettings


def DealWithCutOffs(words, lines):
    i = -1
    while i < len(lines)-2:
        i += 1
        if(lines[i]["Cutoff"]):
            lineText = lines[i]["Text"]
            currentWord = lineText[len(lineText)-1]

            # get rid of the hyphen
            currentWord["text"] = currentWord["text"][:len(
                currentWord["text"])-1]

            currentWord["chars"].pop(len(currentWord["chars"])-1)

            # add the first "word" of the next line
            nextText = lines[i+1]["Text"]
            nextWord = nextText[0]

            for char in nextWord["chars"]:
                currentWord["chars"].append(char)

            currentWord["text"] += nextWord["text"]

            # remove the first word from the next line
            lines[i+1]["Text"].pop(0)
            words.pop(lines[i+1]["LineStartDex"])
            if(len(lines[i+1]["Text"]) == 0):
                lines.pop(i+1)
            lines[i+1]["LineEndDex"] -= 1
            for j in range(i+2, len(lines)):
                lines[j]["LineStartDex"] -= 1
                lines[j]["LineEndDex"] -= 1

            # update this line
            lineText[len(lineText)-1] = currentWord
            lines[i]["Text"] = lineText
    return words, lines


# returns True if words[w] is on a newline
def newline(words, w, error):
    if w == 0 or w >= len(words)-1:
        return False
    prevTop = float(words[w-1]["top"])
    top = float(words[w]["top"])
    if(minorfunctions.areEqual(top, prevTop, error)):
        return False
    bot = float(words[w]["bottom"])
    prevBot = float(words[w-1]["bottom"])
    if(minorfunctions.listElementsEqual([bot, prevBot], error)):
        return False
    return True


# adds the contents of a section header to another section
# tomove is Section header whose contents will be moved.
# destination is a Section header who will receive tomove's contents.
# tomove's contents will be added at the end of destination
# If destination has subsections, tomove's contents will be added there instead.
def moveSection(tomove, destination):
    check = 0
    if(len(destination.subsections) > 0):
        check = len(destination.subsections[len(
            destination.subsections)-1].subsections)

    if(check == 0):
        for i in range(len(tomove.subsections)):
            destination.subsections.append(
                copy.deepcopy(tomove.subsections[i]))
        for i in range(len(tomove.para)):
            destination.para.append(copy.deepcopy(tomove.para[i]))
        return destination
    else:
        destination.subsections[len(destination.subsections)-1] = moveSection(
            tomove, destination.subsections[len(destination.subsections)-1])
        return destination


# adds the section to PDF
def addSection(header, title, type, PDF, pdfSettings, h=3, pagenum=1, recursionlevel=0):

    coords = copy.copy(pdfSettings.coords)
    # if it's broken return false
    if(type == 0 or header == None or recursionlevel > 9):
        PDF.sections.append(PDFfragments.section(
            "ERROR:SECTION_MISSING" + title, header.parent, pdfSettings.coords))

    # if it's a section header, add it to the PDF's list
    elif(type == 1):
        PDF.sections.append(PDFfragments.section(
            title, header.parent, coords, 1, h, pagenum))

    # if it's the current header's sibling, add it to the parent's list
    elif(type == header.type):
        header.parent.subsections.append(
            PDFfragments.section(title, header.parent, coords, type, h, pagenum))

    # if it's a child of the current header, add it to the current header's list
    elif(type == header.type + 1):
        header.subsections.append(PDFfragments.section(
            title, header, coords, type, h, pagenum))

    # if it's an uncle of the current header, recurse upwards.
    elif(type < header.type):
        if(header.parent and header.parent.parent):
            addSection(header.parent, title, type, PDF,
                       pdfSettings, h, pagenum, recursionlevel+1)
        else:
            PDF.sections.append(PDFfragments.section(
                title, header.parent, coords, h, pagenum))

    # if it's a grandchild of the current header, recurse downwards.
    elif(type > header.type):
        next = header.lastsub()[0]
        if(next):
            addSection(next, title, type, PDF,
                       pdfSettings, h, pagenum, recursionlevel+1)
        else:
            header.subsections.append(
                PDFfragments.section("ERROR:SECTION_MISSING" + title, header, coords, type, h, pagenum))

    return PDF, header


# Intent is to remove running headers at the top of the page that get marked as headers
# This is achieved by removing sections with duplicate headers.
def removeDuplicateHeaders(PDF):
    single = []
    remove = []
    # for each section header, if there's an identical section header, flag both to be removed.
    # each element of remove is (index, sectiontitle)
    for h in range(len(PDF.sections)):
        title = PDF.sections[h].title
        titleinsingle = False

        # check if we've seen this title already
        for i in range(len(single)):
            if(single[i][1] == title):
                titleinsingle = True

        # if we haven't, add it to the list of things we've seen.
        if(not titleinsingle):
            single.append((h, PDF.sections[h].title))

        # if we have, add it to the list of things to remove
        else:
            if h not in remove:
                for j in range(len(single)):
                    if single[j][1] == title and single[j] not in remove:
                        remove.append(single[j])
            remove.append((h, PDF.sections[h].title))

    # now go through and remove them all. Any text under that header will be put under the previous header.
    for i in range(len(remove)-1, -1, -1):
        if(remove[i][0] != 0 and remove[i][0] < len(PDF.sections)-1):
            moveSection(PDF.sections[remove[i][0]],
                        PDF.sections[remove[i][0]-1])
            PDF.sections.pop(remove[i][0])


# removes duplicate sentences.
def removePageHeaderSentences(PDF):
    single = []
    remove = []
    # for each section header, if there's an identical section header, flag both to be removed.
    # each element of remove is (index, sectiontitle)
    for i in range(len(PDF.sections)):
        for j in range(len(PDF.sections[i].para)):
            for k in range(len(PDF.sections[i].para[j].sentences)):

                section = PDF.sections[i]
                para = section.para[j]
                sent = para.sentences[k]

                insingle = False

                # check if we've seen this title already
                for l in range(len(single)):
                    if(single[l].text == sent.text):
                        insingle = True
                        break

                # if we haven't, add it to the list of things we've seen.
                if(not insingle):
                    single.append((sent))

                # if we have, add it to the list of things to remove
                else:
                    if sent not in remove:
                        for l in range(len(single)):
                            if single[l].text == sent.text and single[l] not in remove:
                                remove.append(single[l])
                    remove.append(sent)

    # now go through and remove them all. Any text under that header will be put under the previous header.
    for i in range(len(remove)-1, -1, -1):
        sent = remove[i]
        PDF.sections[sent.coords[0]] = recursiveRemoveSentence(
            PDF.sections[sent.coords[0]], sent.coords, sent.para, sent.sentNum)
    return PDF


# removes a sentence from a section at the given coords, para, and sent
# it will navigate itself to the correct subsection before trying to remove the sentence.
def recursiveRemoveSentence(section, coords, paraNum, sentNum):
    if(len(coords) == 0):
        return section
    elif(len(coords) == 1):
        section.para[paraNum].sentences.pop(sentNum)
        if(len(section.para[paraNum].sentences) == 0):
            section.para.pop(paraNum)
        return section
    else:
        section = section.subsections[coords[0]]
        return recursiveRemoveSentence(section, coords[1:], paraNum, sentNum)


# Same as "recursiveRemoveSentence" but for paragraphs
def recursiveRemovePara(section, coords, paraNum):
    if(len(coords) == 0 or paraNum >= len(section.para)):
        return section
    if(len(coords) == 1):
        section.para.pop(paraNum)
        if paraNum < len(section.para):
            if len(section.para[paraNum].sentences) == 0:
                section.para.pop(paraNum)
        for i in range(len(section.para)):
            if(section.para[i].paraNum > paraNum):
                section.para[i].paraNum -= 1
                for j in range(len(section.para[i].sentences)):
                    section.para[i].sentences[j].para -= 1
        return section
    elif(len(section.subsections) > coords[0]):
        section = section.subsections[coords[1]]
        return recursiveRemoveSentence(section, coords[1:], paraNum, sentNum)
    else:
        return section

# removes any headers that are actually just figure or table descriptions.
# figures and graphics get added to PDF.figures
# tables get added to PDF.tables


def removeFigureHeaders(PDF):
    if(len(PDF.sections) <= 1):
        return PDF

    nlp = spacy.load("en_core_web_sm")

    i = -1
    while i < len(PDF.sections)-1:
        i += 1
        doc = nlp(PDF.sections[i].title)
        if(len(doc) > 1 and i > 0):
            if(doc[1].text.isdigit() or doc[1].text == "." and doc[2].text.isdigit()):
                PDF.sections[i] = DealWithMultiLineFigureHeader(
                    PDF.sections[i])

                PDF.sections[i -
                             1] = moveSection(PDF.sections[i], PDF.sections[i-1])
                PDF.sections.pop(i)
                i -= 1

        PDF, PDF.sections[i] = recursiveRemoveFigureHeaders(
            PDF, PDF.sections[i])
        PDF.sections[i] = cleanSection(PDF.sections[i])
    return PDF


# In the event that a figure header goes onto multiple lines, this will remove all of them.
def DealWithMultiLineFigureHeader(section):

    if(len(section.para) == 0 or len(section.para[0].sentences) == 0):
        return section

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(section.para[0].sentences[0].text)

    if(doc[0].is_lower):
        section.title += section.para[0].sentences[0].text
        section.para[0].sentences.pop(0)

    return section

# removes figure descriptions that are subsection headers or are in text


def recursiveRemoveFigureHeaders(PDF, section):
    i = -1
    while i < len(section.para)-1:
        i += 1
        para = section.para[i]
        if(len(para.sentences) == 0):
            section.para.pop(i)
            i -= 1
            continue
        if(len(para.sentences) == 1):
            continue
        sent = minorfunctions.words(para.sentences[0].text)
        sent2 = minorfunctions.words(para.sentences[1].text)
        if(len(sent) == 2 and sent[1].isdigit() or len(sent) == 1 and sent2[0].isdigit()):
            PDF.figures.append(para)
            if(len(section.coords) > 1):
                PDF.sections[section.coords[0]] = recursiveRemovePara(
                    section, section.coords[1:], para.paraNum)
                section = PDF.sections[section.coords[0]]
            else:
                PDF.sections[section.coords[0]].para.pop(para.paraNum)
            i -= 1

    for j in range(len(section.subsections)-1):
        PDF, section.subsections[j] = recursiveRemoveFigureHeaders(
            PDF, section.subsections[j])
    return PDF, section


# cleanSection takes a section and removes empty paragraphs and stitches fragmented ones together.
def cleanSection(section):
    nlp = spacy.load("en_core_web_sm")
    i = -1
    while i < len(section.para):
        i += 1
        if(i > len(section.para)-1):
            break
        para = section.para[i]
        prev = section.para[i-1]
        if(len(para.sentences) == 0):
            section.para.pop(i)
            i -= 1
            continue
        doc = nlp(section.para[i].sentences[0].text)
        if(doc[0].is_lower):
            prev.sentences[len(prev.sentences) -
                           1].text += para.sentences[0].text
            for j in range(1, len(para.sentences)):
                prev.sentences.append(para.sentences[j])
            section.para[i] = para
            section.para[i-1] = prev
            section.para.pop(i)
            i -= 1
    i = -1
    while i < len(section.subsections)-1:
        i += 1
        if(len(section.subsections[i].subsections) == 0):
            if(len(section.subsections[i].para) == 0):
                section.subsections.pop(i)
                i -= 1
                continue
        section.subsections[i] = cleanSection(section.subsections[i])
    return section


# use this instead of the default pdfplumber.extract_text()
# extract text only looks at the doctop attribute, which makes it not read subscript right
# page is pdf.pages[i] via pdfplumber
# hError is an integer
# spaceChar is for if words are delineated by space characters instead of just physical space

def getWords(page, hError, spaceChar=False, vError=3):
    chars = page.chars
    pagenum = str(page.page_number)
    retval = []
    bookmark = 0
    if(len(chars) == 0):
        return []

    if(spaceChar):
        hError = 60

    space = minorfunctions.mostCommon(minorfunctions.reverseArr(
        chars, "width")) * decimal.Decimal((hError)/100)

    i = -1
    unusual = ""
    while i < len(chars)-2:
        i += 1

        if(isSpace(chars, i) and not spaceChar and len(retval) < 30):
            return getWords(page, hError, True)

        if(isSpace(chars, i) and bookmark != i):
            if(unusual != ""):
                unusual = ""
            else:
                unusual = findScript(chars, i, bookmark-1,
                                     vError, float(space)*4)

            word = makeWord(chars[bookmark:i+1], unusual)
            retval, bookmark = addWord(word, retval, unusual, bookmark, i)

        elif(chars[i+1]["x0"]+space < chars[i]["x1"]):
            if(unusual != ""):
                unusual = ""
            else:
                unusual = findScript(chars, i, bookmark-1,
                                     vError, float(space)*4)

            word = makeWord(chars[bookmark:i+1], unusual)
            retval, bookmark = addWord(word, retval, unusual, bookmark, i)

        else:
            section = chars[bookmark:i+1]
            topUnEqual = not minorfunctions.areEqual(
                chars[i+1]["top"], chars[i]["top"], vError)
            botUnEqual = not minorfunctions.areEqual(
                chars[i+1]["bottom"], chars[i]["bottom"], vError)
            horizontalSpace = not minorfunctions.areEqual(
                chars[i+1]["x0"], chars[i]["x1"], space)

            if(topUnEqual or botUnEqual or (not spaceChar and horizontalSpace)):
                if(pagenum == '1'):
                    print("Breakpoint")
                if(unusual != ""):
                    unusual = ""
                else:
                    unusual = findScript(chars, i, bookmark-1,
                                         vError, float(space)*4)

                word = makeWord(chars[bookmark:i+1], unusual)
                retval, bookmark = addWord(word, retval, unusual, bookmark, i)

    if(bookmark != len(chars)-1):
        retval.append(makeWord(chars[bookmark:len(chars)]))

    return retval


# returns true if its a space or a wacky character that ends up looking like a space.
def isSpace(chars, i):
    if(i == 0 or i > len(chars)-1):
        return False
    if(chars[i]["text"] == ' ' or chars[i]["text"] == '\xa0'):
        return True
    return False


# takes characters and turns them into a word object that pdfplumber would use.
def makeWord(chars, unusual=""):
    if(len(chars) == 0):
        return None

    if(unusual == "Superscript"):
        text = "^{"
    elif(unusual == "Subscript"):
        text = "_{"
    else:
        text = ""

    for c in range(len(chars)):
        if(isSpace(chars, c)):
            x0 = chars[0]["x0"]
            x1 = chars[c-1]["x1"]

            top = minorfunctions.toppest(chars)["top"]
            bottom = minorfunctions.bottomest(chars)["bottom"]

            sub = False
            super = False
            if(unusual == "Subscript"):
                sub = True
                text += "}"
            if(unusual == "Superscript"):
                super = True
                text += "}"

            retval = {"text": text, "chars": chars[:c], "x0": x0, "x1": x1, "top": top,
                      "bottom": bottom, "upright": True, "direction": 1, "Subscript": sub, "Superscript": super}
            return retval
        else:
            text += chars[c]["text"]

    x0 = chars[0]["x0"]
    x1 = chars[len(chars)-1]["x1"]

    top = minorfunctions.toppest(chars)["top"]
    bottom = minorfunctions.bottomest(chars)["bottom"]

    if(unusual == "Subscript"):
        sub = True
        text += "}"
    if(unusual == "Superscript"):
        super = True
        text += "}"

    retval = {"text": text, "chars": chars, "x0": x0, "x1": x1, "top": top,
              "bottom": bottom, "upright": True, "direction": 1}
    return retval


def addLine(lines, words, prevLineBegin, currentLineBegin, nextLineBegin, w):
    if(len(words) == 0):
        return lines, prevLineBegin, currentLineBegin, nextLineBegin

    hate = words[300:]

    prevline = words[prevLineBegin:currentLineBegin]
    currentline = words[currentLineBegin:nextLineBegin]
    nextline = words[nextLineBegin:w]

    if(len(prevline) > 0):
        prevBottom = float(minorfunctions.bottomest(prevline)["bottom"])
        prevTop = float(minorfunctions.toppest(prevline)["top"])

    currentBottom = float(minorfunctions.bottomest(currentline)["bottom"])
    currentTop = float(minorfunctions.toppest(currentline)["top"])

    if(len(nextline) > 0):
        nextBottom = float(minorfunctions.bottomest(nextline)["bottom"])
        nextTop = float(minorfunctions.toppest(nextline)["top"])

    if(len(lines) == 0):
        aftspace = nextTop - currentBottom
        befspace = aftspace * 3

    elif(nextLineBegin == len(words)):
        befspace = currentTop - prevBottom
        aftspace = befspace * 3

    else:
        aftspace = nextTop - currentBottom
        befspace = currentTop - prevBottom

    cutoff = False
    charDex = 1
    chars = words[nextLineBegin - 1]["chars"]
    char = chars[len(chars)-charDex]
    while(isSpace(chars, len(chars)-charDex)):
        charDex += 1
        char = chars[len(chars)-charDex]
    if(char["text"] == '-'):
        cutoff = True

    height = float(minorfunctions.bottomest(currentline)
                   ["bottom"] - minorfunctions.toppest(currentline)["top"])

    aftRatio = height/aftspace
    befRatio = height/befspace
    lines.append({"LineStartDex": currentLineBegin, "LineEndDex": nextLineBegin-1, "AftSpace": aftspace,
                 "BefSpace": befspace, "Height": height, "AftRatio": aftRatio, "BefRatio": befRatio,
                  "Align": words[currentLineBegin]["x0"], "Text": words[currentLineBegin:nextLineBegin], "Cutoff": cutoff})

    prevLineBegin = currentLineBegin
    currentLineBegin = nextLineBegin
    nextLineBegin = w

    return lines, prevLineBegin, currentLineBegin, nextLineBegin


# figures out a bunch of information about the section and then adds it
# info includes type, parent, coords, etc
def registerSection(PDF, words, w, lines, lineIndex, pdfSettings, pagenum):

    pdfSettings.addto = False
    pdfSettings.consistentRatio = 0

    type = textprocessing.FindsectionType(
        words[pdfSettings.bookmark], pdfSettings.activesection, pagenum, lines[lineIndex]["Height"], pdfSettings.intraline)

    if(len(lines[lineIndex]["Text"]) < 2 and len(lines[lineIndex]["Text"][0]["text"]) < 3):
        type = pdfSettings.activesection.type + 1

    pdfSettings.coords = minorfunctions.newCoords(
        pdfSettings.coords, type)

    PDF, pdfSettings.activesection = addSection(pdfSettings.activesection,
                                                textprocessing.makeString(words[pdfSettings.bookmark:w+1]), type, PDF, pdfSettings, lines[lineIndex]["Height"], pagenum, pdfSettings.intraline)

    pdfSettings.activesection = minorfunctions.updateActiveSection(
        PDF, words, pdfSettings)

    pdfSettings.paraNum = 0
    pdfSettings.bookmark = w+1

    return PDF, pdfSettings, lines


def addBlock(pdfSettings, words, w):
    pdfSettings.addto = False
    sentlist = textprocessing.MakeSentences(textprocessing.makeString(
        words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)

    if(w < len(words)-1):
        para = PDFfragments.paragraph(
            copy.copy(pdfSettings.coords), pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites), words[w+1]["x0"])
    else:
        para = PDFfragments.paragraph(
            copy.copy(pdfSettings.coords), pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites), words[w]["x0"])
    pdfSettings.cites = []
    pdfSettings.activesection.para.append(para)
    pdfSettings.paraNum += 1
    pdfSettings.bookmark = w+1

    return pdfSettings


# turns sentlist into a paragraph and adds it to the last para in pdfSettings.activesection
# returns updated pdfSettings
def addToPara(pdfSettings, sentlist, words, w):
    activepara = pdfSettings.activesection.para[len(
        pdfSettings.activesection.para)-1]
    while(len(activepara.sentences) == 0):
        pdfSettings.activesection.para.pop(len(
            pdfSettings.activesection.para)-1)
        if(len(pdfSettings.activesection.para) == 0):
            return addPara(pdfSettings, sentlist, words, w)
        activepara = pdfSettings.activesection.para[len(
            pdfSettings.activesection.para)-1]
    for s in range(len(sentlist)):
        if(s == 0):
            activepara.sentences[len(
                activepara.sentences)-1].text += " " + sentlist[s].text
        else:
            pdfSettings.activesection.para[len(
                pdfSettings.activesection.para)-1].sentences.append(sentlist[s])

    return pdfSettings


# turns sentlist into a paragraph and adds it to pdfSettings.activesection
# returns updated pdfSettings
def addPara(pdfSettings, sentlist, words, w):
    if(w < len(words)-1):
        para = PDFfragments.paragraph(
            copy.copy(pdfSettings.coords), pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites), words[w+1]["x0"])
    else:
        para = PDFfragments.paragraph(
            copy.copy(pdfSettings.coords), pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites), words[w]["x0"])
    pdfSettings.cites = []
    pdfSettings.activesection.para.append(para)
    pdfSettings.paraNum += 1

    return pdfSettings

# takes the words between pdfSettings.bookmark and w and turns them into a paragraph
# adds the paragraph to pdfSettings.activesection (or combines it with last paragraph if addto is True)
# returns updated pdfSettings.


def extensiveAddPara(pdfSettings, words, w):
    if(w < 0):
        return pdfSettings

    sentlist = textprocessing.MakeSentences(textprocessing.makeString(
        words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)

    sentlist, pdfSettings = textprocessing.cleanPara(sentlist, pdfSettings)

    # if this is the 2nd half of a cutoff paragraph, sew it back together.
    if(pdfSettings.addto and len(pdfSettings.activesection.para) > 0):
        pdfSettings.addto = False
        pdfSettings = addToPara(pdfSettings, sentlist, words, w)
    else:
        pdfSettings = addPara(pdfSettings, sentlist, words, w)
    pdfSettings.bookmark = w+1

    return pdfSettings


def registerFigure(PDF, lines, lineIndex, words, pdfSettings, pagenum):
    # if it follows the "new figure" format, then add a new one, otherwise, add to the last one.
    line = lines[lineIndex]
    if(len(line["Text"]) > 1):
        text0 = line["Text"][0]["text"]
        text1 = line["Text"][1]["text"]
        bigenough = len(line["Text"]) >= 2
        numbered = text1.isdigit() or text1[:len(text1)-1].isdigit()
        figure = minorfunctions.isCaption(text0)
        isNewFigure = (
            figure and bigenough and numbered) or pagenum != PDF.lastFig().pagenum

        if(len(PDF.figures) == 0 or isNewFigure):
            figure = PDFfragments.figure(line["Text"], pagenum)
            PDF.figures.append(figure)
        else:
            PDF.figures[len(PDF.figures)-1].addWords(line["Text"])

    else:
        if(len(PDF.figures) > 0 and pagenum == PDF.lastFig().pagenum):
            PDF.figures[len(PDF.figures)-1].addWords(line["Text"])
        else:
            figure = PDFfragments.figure(line["Text"], pagenum)
            PDF.figures.append(figure)

    for i in range(line["LineEndDex"], line["LineStartDex"]-1, -1):
        words.pop(i)

    lines = updateIndices(lines, lineIndex)
    lines.pop(lineIndex)

    return PDF, pdfSettings, lines, words


# shift the indices of lines after lineIndex so that lineIndex can be safely removed from lines.
# returns updated lines.
def updateIndices(lines, lineIndex):
    if(lineIndex < 0 or lineIndex >= len(lines)):
        return lines

    line = lines[lineIndex]
    size = line["LineEndDex"] - line["LineStartDex"] + 1

    for i in range(lineIndex, len(lines)):
        lines[i]["LineEndDex"] -= size
        lines[i]["LineStartDex"] -= size

    return lines


# detects whether chars[i] is superscript or subscript.
def findScript(chars, i, bookmark, error, width):
    if(i == 0):
        return ""
    char = chars[i]
    compare = chars[bookmark]

    # if(not minorfunctions.isLesser(char["width"], width)):
    #    return ""

    topdiff = char["top"] - compare["top"]
    botdiff = char["bottom"] - compare["bottom"]

    if(topdiff == 0 or botdiff == 0):
        return ""

    if(topdiff > 0.1 and minorfunctions.isLesser(topdiff, char["height"], error, True)):
        return "Subscript"

    if(botdiff < -0.1 and minorfunctions.isLesser(float(botdiff)*-1, char["height"], error, True)):
        return "Superscript"

    return ""


def addWord(word, words, unusual, bookmark, i):
    if(word):
        if(unusual == ""):
            words.append(word)
            bookmark = i+1
            return words, bookmark
        else:
            words[len(words)-1]["text"] += word["text"]
            bookmark = i+1
            return words, bookmark

    return words, bookmark
