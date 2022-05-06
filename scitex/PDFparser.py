from tokenize import single_quoted
from typing import Reversible
import pdfplumber
import copy
import re
import PDFfragments
import random
import textprocessing
import minorfunctions
import spacy
from spacy.matcher import Matcher
import textSettings

# This is a document containing all the functions that get used in the code

# mostly cuz I don't wanna look through 5000 lines when I'm looking at code.py

# Sometimes the lines are just a little bit off in terms of how far away they are. I.e. two lines will be 13.7 apart, the next two will be 14.1
ERROR_MARGIN = 3
RATIO_MARGIN = 0.05

# para-margin is the number of unusual spaces that have to happen before I'll believe that they're being used
# to determine different paragraphs.
PARAS_REQUIRED = 2


# MAJOR FUNCTIONS
# The following functions are used to perform major functions and are really long

def getDiffs(words):
    diffs = [[], [], [], []]
    for w in range(len(words)-1):
        # if the first word is lowercase, then a paragraph probably got split up.
        # rework this code so it works on body text and not page sections
        if(w == 0):
            doc = nlp(words[0]["text"])
            if(doc[0].is_lower):
                addto = True

        # diff is the vertical distance from the top of 1 word to the top of the next. If it's not roughly 0, mark a new line.
        # space is the vertical distance from the bottom of 1 word to the top of the next.
        # height is the height of the word.
        # diffs[1] is space
        # diffs[2] is height/space, a relative ratio of its height.
        diff = words[w+1]["top"] - words[w]["top"]

        if(diff - ERROR_MARGIN > 0):
            space = words[w+1]["top"] - words[w]["bottom"]
            height = words[w]["bottom"] - words[w]["top"]
            diffs[0].append(w)
            diffs[1].append(round(float(space), 1))
            diffs[2].append(round(float(height/space), 1))
            diffs[3].append(round(float(height), 1))
    return diffs

# HandleColumns: takes a list of words and separates it by columns.


def HandleColumns(words):
    retval = [[]]
    c = 0

    for w in range(1, len(words)):
        if(words[w]["x1"] - words[w-1]["x0"] + ERROR_MARGIN > words[w-1]["x1"] - words[w-2]["x0"]
                and words[w-1]["top"] + ERROR_MARGIN > words[w]["top"]):
            c += 1
        if(words[w]["top"] + ERROR_MARGIN > words[w-1]["top"]):
            c = 0
        while(c > (len(retval) - 1)):
            retval.append([])
        retval[c].append(words[w])
    return retval
    # idea for separating multiple columns

    # add remaining words in this line to a "next column" list which will be handled after the current column.

# FindSpace: Takes a PDF and tries to figure out what the spacing is
# returns linespace, paraAlign, paraSpace
# linespace is the space between lines
# paraAlign is the left-margin on a standard line, so that any deviation can be
# detected as a new paragraph
# paraSpace is the vertical space between paragraphs, if that spacing is not the same as linespace.


def FindSpace(pdf):

    # For now we're going to use the first three pages, because if there are 3 pages without a
    # normal line space; paragraph space; and a section space, then too bad. (for now)
    words = []
    words.append(pdf.pages[0].extract_words(y_tolerance=3))
    words.append(pdf.pages[1].extract_words(y_tolerance=3))
    words.append(pdf.pages[2].extract_words(y_tolerance=3))

    # for each word, if it has a different y coordinate, note the difference
    # diffs[0] is the distance between lines
    # diffs[1] is the index of the last word of the previous line
    # diffs[2] is the first index of each line
    # diffs[3] is the left-alignment of the first word of each line
    # diffs[4] is, for each line, the height of that line divided by the space between that line and the next line.
    # diffs[5] is the height of each line
    diffs = [[], [], [], [], [], []]

    for i in range(len(words)):
        bookmark = 0
        for j in range(1, len(words[i])):
            if(words[i][j-1]["top"] != words[i][j]["top"]):
                diff = words[i][j]["top"] - words[i][j-1]["bottom"]
                height = words[i][j]["bottom"] - words[i][j]["top"]
                diffs[0].append(float(diff))
                diffs[1].append(bookmark)
                diffs[2].append(j-1)
                diffs[3].append(int(words[i][j]["x0"]))
                diffs[4].append(round(float(height/diff), 2))
                diffs[5].append(float(height))
                bookmark = j

    # the most common difference is going to be the difference between one line and another.
    # True means we want an index and not the most common value.
    lineIndex = minorfunctions.mostCommon(diffs[0], True)
    linespace = round(float(diffs[0][lineIndex]), 1)
    lineratio = round(float(diffs[4][lineIndex]), 1)
    lineheight = round(float(diffs[5][lineIndex]), 1)
    # paraAlign should be the x coordinate of the body text, so that any line with a different x-coordinate can be a new paragraph.

    paraSpace = -1
    paraAlign = -1
    paraCount = 0

    for d in range(1, len(diffs[0])-1):
        if(diffs[0][d-1] - linespace < ERROR_MARGIN and diffs[0][d+1] - linespace < ERROR_MARGIN and diffs[0][d] - linespace > ERROR_MARGIN):
            paraSpace = diffs[0][d]
            paraCount = 0

    if(paraCount < PARAS_REQUIRED):
        paraSpace = -1

    if(paraSpace == -1):
        paraAlign = diffs[3][lineIndex]

    list = []
    for i in range(len(diffs[0])):
        if(diffs[0][i] == linespace):
            list.append(diffs[1][i])

    return linespace, lineratio, lineheight, paraAlign, paraSpace


# PDFSort: Takes a pdf from pdfplumber, a PDF class from above, and two numbers to calibrate reading.
def PDFSort(pdf):

    # declare variables that get used later.
    PDF = PDFfragments.PDFdocument()
    nlp = spacy.load("en_core_web_sm")
    activesection = PDFfragments.section("")
    coords = [-1]
    paraNum = 0
    addto = False
    cites = []
    diffsIndex = 0
    paraAlign = -1
    paraSpace = -1
    useSpace = False
    consistentRatio = 0

    # Find out what the spacing looks like for the pdf
    linespace, lineratio, lineheight, paraAlign, paraSpace = FindSpace(pdf)

    if(paraAlign == -1):
        useSpace = True

    settings = pdf.metadata

# big loop through each page. Get the page's text, then sort out the paragraphs and sections

    for pg in range(len(pdf.pages)):
        page = (pdf.pages[pg].extract_words(y_tolerance=6))
        cols = HandleColumns(page)

        # do this entire process for each column
        for c in range(len(cols)):

            # reset the bookmark
            # words = all words in this col
            # diffs = a list of lines of text and some accompanying stats.
            bookmark = 0
            words = cols[c]
            diffs = getDiffs(words)

            for d in range(len(diffs[0])):

                # w is the index of the first word of each line
                w = diffs[0][d]
                if(w > len(words)-1):
                    w = len(words)-1

                if(pg == 6):
                    print("stop")

                # Use that stuff to figure out what type of text we're working with
                setting = textSettings.diffSettings(
                    d, diffs, lineheight, lineratio, consistentRatio, ERROR_MARGIN)

                # if it's normal, we don't care.
                # if it's the end of a section, then add as normal, reset consistent
                # if it's at the beginning of a multi, set consistent space and don't move bookmark.
                # if it's in a multi, don't move bookmark.

                if(settings.type == diffType.START_MULTI):
                    consistentRatio = ratio
                # if we're expecting a section and the next line is not a section, add the section
                elif(settings.type == diffType.END_SECTION):

                    # if next line is relative normal space, multiline
                    # else, single line.
                    consistentRatio = 0
                    if(bookmark < len(words)):
                        # Figure out what type of section it is and add it appropriately:
                        type = textprocessing.FindsectionType(words[bookmark])

                        addSection(activesection,
                                   textprocessing.makeString(words[bookmark:w+1]), type, PDF)

                        # update activesection
                        activesection = PDF.lastSect()
                        test = activesection.lastsub()
                        while(test != (None, None)):
                            activesection = test[0]
                            test = activesection.lastsub()

                        activesection.type = textprocessing.FindsectionType(
                            words[bookmark])

                        # update coordinates
                        coords = newCoords(coords, type)

                        # reset paragraph counter, update bookmark
                        paraNum = 0
                        bookmark = w+1

                # if it's the end of a non-section block, add that block as a paragraph.
                elif(settings.type == diffType.END_BLOCK):
                    sentlist = textprocessing.MakeSentences(textprocessing.makeString(
                        words[bookmark:w+1]), copy.copy(coords), paraNum)
                    if(w < len(words)-1):
                        para = PDFfragments.paragraph(
                            copy.copy(coords), paraNum, sentlist, copy.copy(cites), words[w+1]["x0"])
                    else:
                        para = PDFfragments.paragraph(
                            copy.copy(coords), paraNum, sentlist, copy.copy(cites), words[w]["x0"])
                    cites = []
                    activesection.para.append(para)
                    paraNum += 1
                    bookmark = w+1
                # if there's a new paragraph, add that.
                elif (textprocessing.DetermineParagraph(words, w, paraAlign, paraSpace, useSpace, ERROR_MARGIN)):
                    sentlist = textprocessing.MakeSentences(textprocessing.makeString(
                        words[bookmark:w+1]), copy.copy(coords), paraNum)
                    # if this is the 2nd half of a cutoff paragraph, sew it back together.
                    if(addto and pg > 0):
                        addto = False
                        for s in range(len(sentlist)):
                            activepara = activesection.para[len(
                                activesection.para)-1]
                            if(s == 0):
                                activepara.sentences[len(
                                    activepara.sentences)-1].text += " " + sentlist[s].text
                            else:
                                activesection.para[len(
                                    activesection.para)-1].sentences.append(sentlist[s])
                    else:
                        if(w < len(words)-1):
                            para = PDFfragments.paragraph(
                                copy.copy(coords), paraNum, sentlist, copy.copy(cites), words[w+1]["x0"])
                        else:
                            para = PDFfragments.paragraph(
                                copy.copy(coords), paraNum, sentlist, copy.copy(cites), words[w]["x0"])
                        cites = []
                        activesection.para.append(para)
                        paraNum += 1
                    bookmark = w+1

            # END OF DIFFS LOOP
            # Add whatever text is at the end of the page.
            if(bookmark != len(words)-1):
                sentlist = textprocessing.MakeSentences(textprocessing.makeString(
                    words[bookmark:w+1]), copy.copy(coords), paraNum)
                if(addto):
                    addto = False
                    if(len(activesection.para) == 0):
                        newpara = PDFfragments.paragraph(coords, paraNum)
                        activesection.para.append(newpara)
                    activepara = activesection.para[len(
                        activesection.para)-1]
                    for s in range(len(sentlist)):
                        if(s == 0):
                            activepara.sentences[len(
                                activepara.sentences)-1].text += " " + sentlist[s].text
                        else:
                            activesection.para[len(
                                activesection.para)-1].sentences.append(sentlist[s])
                else:
                    para = PDFfragments.paragraph(
                        copy.copy(coords), paraNum, sentlist, copy.copy(cites))
                    cites = []
                    activesection.para.append(para)
                    paraNum += 1
                bookmark = 0

    removePageHeaders(PDF)
    # removeFigureHeaders(PDF)

    return PDF


def addSection(header, title, type, PDF=None):
    type = textprocessing.FindsectionType(title)
    # if it's broken return false
    if(type == 0 or header == None):
        PDF.sections.append(PDFfragments.section(
            "ERROR:SECTION_MISSING" + title, header.parent))

    # if it's a section header, add it to the PDF's list
    elif(type == 1):
        PDF.sections.append(PDFfragments.section(title, header.parent))

    # if it's the current header's sibling, add it to the parent's list
    elif(type == header.type):
        header.parent.subsections.append(
            PDFfragments.section(title, header.parent))

    # if it's a child of the current header, add it to the current header's list
    elif(type == header.type + 1):
        header.subsections.append(PDFfragments.section(title, header))

    # if it's an uncle of the current header, recurse upwards.
    elif(type < header.type):
        if(header.parent and header.parent.parent):
            addSection(header.parent, title, type, PDF)
        else:
            PDF.sections.append(PDFfragments.section(title, header.parent))

    # if it's a grandchild of the current header, recurse downwards.
    elif(type > header.type):
        next = header.lastsub()[0]
        if(next):
            addSection(next, title, type)
        else:
            header.subsections.append(
                PDFfragments.section("ERROR:SECTION_MISSING" + title, header))


# update the coordinates
def newCoords(coords, type):
    newcoords = []
    # if we're in a shallower section now (from 2.3.4.5 to 3.1) remove depth
    if(len(coords) > type):
        for i in range(type):
            newcoords.append(coords[i])
    # if we're in a deeper section, add depth.
    elif(len(coords) < type):
        newcoords = coords
        newcoords.append(-1)
    # else just copy as is
    else:
        newcoords = coords
    # update coords
    coords = newcoords
    coords[len(coords)-1] += 1
    return coords

# Intent is to remove running headers at the top of the page that get marked as headers
# This is achieved by removing sections with duplicate headers.


def removePageHeaders(PDF):
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


# removes any headers that are actually just figure or table descriptions.
# figures and graphics get added to PDF.figures
# tables get added to PDF.tables

def removeFigureHeaders(PDF):
    # set up some spacy stuff
    nlp = spacy.load("en_core_web_sm")
    figurematcher = Matcher(nlp.vocab)
    figurepattern = [{"LOWER": "figure"}, {"IS_DIGIT": True}]
    figpattern = [{"LOWER": "fig"}, {"IS_PUNC": True}, {"IS_DIGIT": True}]
    tablepattern = [{"LOWER": "table"}, {"IS_DIGIT": True}]
    tabpattern = [{"LOWER": "tab"}, {"IS_PUNC": True}, {"IS_DIGIT": True}]
    graphicpattern = [{"LOWER": "graphic"}, {"IS_DIGIT": True}]
    graphpattern = [{"LOWER": "graph"}, {"IS_DIGIT": True}]

    figurematcher.add(
        "figures", [figurepattern, figpattern, tablepattern, tabpattern, graphicpattern, graphpattern])

    for i in range(len(PDF.sections)-1, 0, -1):
        doc = nlp(PDF.sections[i].title)
        matches = figurematcher(doc)

        if len(matches) > 0:
            moveSection(PDF.sections[i], PDF.sections[i-1])
            sectioncopy = PDF.sections[i].copy()
            sectioncopy.parent = PDF.sections[i-1]
            PDF.sections[i-1].subsections.append(sectioncopy)
            PDF.figures.append(sectioncopy.title)
            PDF.sections.pop(i)
