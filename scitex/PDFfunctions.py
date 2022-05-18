import spacy
from spacy.matcher import Matcher
import re
import textprocessing
import PDFfragments
import minorfunctions
import copy

# fix to look at every other page for page headers instead of "every page w/equal text"


def removePageHeadersEarly(words, pdfSettings):
    for i in range(len(pdfSettings.pageHeaders)):
        if(pdfSettings.pageHeaders[i] == words[:len(pdfSettings.pageHeaders[i])]):
            words = CutWords(words, pdfSettings.pageHeaders[i])
            return words
    return words


def CutWords(large, small):
    for i in range(len(small)-1, -1, -1):
        if small[i] == large[i]:
            large.pop(i)
        else:
            return large
    return large


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


def getDiffs(words, pdfSettings, error):
    diffs = []
    bookmark = 0
    for w in range(len(words)-1):
        # if the first word is lowercase, then a paragraph probably got split up.
        if(w == 0):
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(words[0]["text"])
            if(doc[0].is_lower):
                pdfSettings.addto = True

        if(newline(words, w, error)):
            aftspace = float(words[w+1]["top"] - words[w]["bottom"])
            befspace = float(words[w]["top"] - words[bookmark]["bottom"])
            if bookmark == 0:
                befspace = pdfSettings.linespace * 2
            if(len(diffs) == 1):
                diffs[0]["AftSpace"] = befspace
                diffs[0]["AftRatio"] = diffs[0]["Height"]/befspace
            height = float(words[w]["bottom"] - words[w]["top"])
            aftRatio = height/aftspace
            befRatio = height/befspace
            diffs.append({"LineEndDex": w, "AftSpace": aftspace,
                         "BefSpace": befspace, "Height": height, "AftRatio": aftRatio, "BefRatio": befRatio,
                          "Align": words[w]["x0"], "Text": words[bookmark+1:w+1]})
            bookmark = w
    return diffs, pdfSettings

# returns True if words[w] is on a newline


def newline(words, w, error):
    if w == 0:
        return False
    nextTop = float(words[w+1]["top"])
    top = float(words[w]["top"])
    if(minorfunctions.areEqual(top, nextTop, error)):
        return False
    bot = float(words[w]["bottom"])
    prevBot = float(words[w-1]["bottom"])
    nextBot = float(words[w+1]["bottom"])
    if(minorfunctions.listElementsEqual([bot, prevBot, nextBot], error)):
        return False
    return True


# adds the contents of a section header to another section
# tomove is Section header whose contents will be moved.
# destination is a Section header who will receive tomove's contents.
# tomove's contents will be added at the end of destination
# If destination has subsections, tomove's contents will be added there instead.


def moveSection(tomove, destination):
    # check to see if there's a subsection we should be putting this in
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
    else:
        moveSection(
            tomove, destination.subsections[len(destination.subsections)-1])


def addSection(header, title, type, PDF, pdfSettings, recursionlevel=0):

    coords = copy.copy(pdfSettings.coords)
    # if it's broken return false
    if(type == 0 or header == None or recursionlevel > 9):
        PDF.sections.append(PDFfragments.section(
            "ERROR:SECTION_MISSING" + title, header.parent, pdfSettings.coords))

    # if it's a section header, add it to the PDF's list
    elif(type == 1):
        PDF.sections.append(PDFfragments.section(
            title, header.parent, coords))

    # if it's the current header's sibling, add it to the parent's list
    elif(type == header.type):
        header.parent.subsections.append(
            PDFfragments.section(title, header.parent, coords))

    # if it's a child of the current header, add it to the current header's list
    elif(type == header.type + 1):
        header.subsections.append(PDFfragments.section(
            title, header, coords))

    # if it's an uncle of the current header, recurse upwards.
    elif(type < header.type):
        if(header.parent and header.parent.parent):
            addSection(header.parent, title, type, PDF,
                       pdfSettings, recursionlevel+1)
        else:
            PDF.sections.append(PDFfragments.section(
                title, header.parent, coords))

    # if it's a grandchild of the current header, recurse downwards.
    elif(type > header.type):
        next = header.lastsub()[0]
        if(next):
            addSection(next, title, type, PDF, pdfSettings, recursionlevel+1)
        else:
            header.subsections.append(
                PDFfragments.section("ERROR:SECTION_MISSING" + title, header, coords))


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
    else:
        section = section.subsections[coords[0]]
        return recursiveRemoveSentence(section, coords[1:], paraNum, sentNum)


# removes any headers that are actually just figure or table descriptions.
# figures and graphics get added to PDF.figures
# tables get added to PDF.tables

def removeFigureHeaders(PDF):
    if(len(PDF.sections) == 0):
        return PDF
    else:
        for i in range(len(PDF.sections)):
            if i == 6:
                print("Breakpoint")
            PDF, PDF.sections[i] = recursiveRemoveFigureHeaders(
                PDF, PDF.sections[i])
            PDF.sections[i] = cleanSection(PDF.sections[i])
    return PDF


def recursiveRemoveFigureHeaders(PDF, section):
    i = -1
    while i < len(section.para)-1:
        i += 1
        para = section.para[i]
        if(len(para.sentences) == 0):
            section.para.pop(i)
            i -= 1
            continue
        sent = words(para.sentences[0].text)
        sent2 = words(para.sentences[1].text)
        if(len(sent) == 2 and sent[1].isdigit() or len(sent) == 1 and sent2[0].isdigit()):
            PDF.figures.append(para)
            PDF.sections[section.coords[0]] = recursiveRemovePara(
                section, section.coords, para.paraNum)
            i -= 1

    for j in range(len(section.subsections)-1):
        PDF, section.subsections[j] = recursiveRemoveFigureHeaders(
            PDF, section.subsections[j])
    return PDF, section


# "." counts
# "(x* . x*)" doesn't count

def cleanSection(section):
    nlp = spacy.load("en_core_web_sm")
    i = 0
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
    for i in range(len(section.subsections)):
        section.subsections[i] = cleanSection(section.subsections[i])
    return section


def words(str):
    retval = []
    bookmark = 0
    for i in range(len(str)):
        if str[i] == ' ' or str[i] == '.':
            retval.append(str[bookmark:i])
            bookmark = i+1
    return retval
