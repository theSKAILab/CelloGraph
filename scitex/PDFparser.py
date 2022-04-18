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
    activesection = PDFfragments.section("", None)
    activesubsection = PDFfragments.section("", None)
    activesection = PDFfragments.section("", None)
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

# Currently these two lines make it so that we only do page 2, for debugging purposes.
# They have to be changed back to len(pages) and pg later.
    for pg in range(len(pdf.pages)):
        page = (pdf.pages[pg].extract_words(y_tolerance=6))
        catch = False
        cols = HandleColumns(page)

        sectionwatch = True

        # we're making a new diffs list
        # 0 is the end of the previous line
        # 1 is the space between the lines
        # 2 is the ratio between height and space
        # 3 is height

        diffs = [[], [], [], []]

        # do this entire process for each column
        for c in range(len(cols)):

            # reset the bookmark
            # words = all words in this col
            bookmark = 0
            words = cols[c]

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

            for d in range(len(diffs[0])):

                # w is the index of the first word of each line
                w = diffs[0][d]
                if(w > len(words)-1):
                    w = len(words)-1

                if(pg == 4):
                    print("bruh")

                # diff is the difference between top of this line and bottom of previous line
                # ratio is the height/space ratio
                # height is how tall this line is.
                diff = diffs[1][d]
                ratio = diffs[2][d]
                height = diffs[3][d]

                # Figure out a bunch of stuff

                # is the text big
                big_size = False
                small_size = False
                normal_size = False
                if(height > lineheight + ERROR_MARGIN):
                    big_size = True
                elif(height < lineheight - ERROR_MARGIN):
                    small_size = True
                else:
                    normal_size = True

                # is there a big space beforehand
                before_bigspace = False
                before_smallspace = False
                before_normal = False
                if(d != 0):
                    if(diffs[1][d-1] > linespace + ERROR_MARGIN):
                        before_bigspace = True
                    elif(diffs[1][d-1] < linespace - ERROR_MARGIN):
                        before_smallspace = True
                    else:
                        before_normal = True

                # is there a big space afterwards
                after_bigspace = False
                after_smallspace = False
                after_normal = False
                if(diffs[1][d] > linespace + ERROR_MARGIN):
                    after_bigspace = True
                elif(diffs[1][d] < linespace - ERROR_MARGIN):
                    after_smallspace = True
                else:
                    after_normal = True

                # Use that stuff to figure out what type of text we're working with

                single_section = False
                start_multi = False
                in_multi = False
                end_section = False
                figure_text = False
                normal_text = False
                end_block = False

                if(bookmark == 0):
                    before_bigspace = True

                # if we're in a multiline section then figure out whether it's ending.
                if(consistentRatio != 0):
                    if(d < len(diffs[1])-1 and diffs[2][d] == consistentRatio and diffs[2][d+1] != lineratio):
                        in_multi = True
                    else:
                        end_section = True
                # if the next line is similar to this line and not normal text, it's a multiline section.
                elif(d < len(diffs[1])-1 and before_bigspace and diffs[2][d+1] == ratio and not diffs[2][d+1] == lineratio):
                    start_multi = True
                # if there's a ton of space before and after this, it's a single line section.
                elif(after_bigspace and before_bigspace):
                    end_section = True
                # if there's a big space but normal text, then it's the end of a block, which we do want to detect.
                elif(after_bigspace):
                    end_block = True
                # if it's none of those, it's normal text.
                else:
                    normal_text = True
                    consistentRatio = 0

                # if it's normal, we don't care.
                # if it's the end of a section, then add as normal, reset consistent
                # if it's at the beginning of a multi, set consistent space and don't move bookmark.
                # if it's in a multi, don't move bookmark.

                if(start_multi):
                    consistentRatio = ratio
                # if we're expecting a section and the next line is not a section, add the section
                elif(end_section):

                    # if next line is relative normal space, multiline
                    # else, single line.
                    consistentRatio = 0
                    if(bookmark < len(words)):
                        # Figure out what type of section it is and add it appropriately:
                        # add it to the list of sections and update activesection, subsection, section
                        type = textprocessing.FindsectionType(words[bookmark])
                        # sections
                        if(type == 1):
                            PDF.sections.append(
                                PDFfragments.section(textprocessing.makeString(words[bookmark:w+1]), None, type, ratio))
                            activesection = PDF.sections[len(PDF.sections)-1]
                            activesection = activesection
                        # subsection
                        elif(type == 2):
                            activesection.subsections.append(
                                PDFfragments.section(textprocessing.makeString(words[bookmark:w+1]), PDF.sections[len(PDF.sections)-1], type))
                            activesubsection = activesection.subsections[len(
                                activesection.subsections)-1]
                            activesection = activesubsection
                        # Some form of sub-sub-section
                        else:
                            # if activesection isn't a section
                            if(activesection.parent):
                                # if this section is at the same level as activesection (i.e. both are x.y.z) then
                                # add new section as activesection's sibling
                                if(type == activesection.type):
                                    activesection.parent.subsections.append(
                                        PDFfragments.section(minorfunctions.makeString(words[bookmark:w+1]), PDF.sections[len(PDF.sections)-1].subsections[len(activesection.subsections)-1], type))
                                    activesection = activesection.parent.subsections[len(
                                        activesection.parent.subsections)-1]
                                # if this section is lower than activesection (i.e. AS is x.y.z and this is x.y.z.a)
                                # add new section as a subsection of activesection.
                                elif(type > activesection.type):
                                    activesection.subsections.append(PDFfragments.section(
                                        textprocessing.makeString(words[bookmark:w+1]), activesection, type))
                            # if activesection is a section
                            # add new section as a subsection of that section.
                            else:
                                activesection.subsections.append(
                                    PDFfragments.section(textprocessing.makeString(words[bookmark:w+1]), PDF.sections[len(PDF.sections)-1]))
                                activesubsection = activesection.subsections[len(
                                    activesection.subsections)-1]
                                activesection = activesubsection
                        # update the coordinates
                        newcoords = []
                        # if we're in a shallower section now (from 2.3.4.5 to 3.1) remove depth
                        if(len(coords) > type):
                            for i in range(type):
                                newcoords.append(coords[i])
                        # if we're in a deeper section, add depth.
                        elif(len(coords) < type):
                            newcoords = copy.copy(coords)
                            newcoords.append(-1)
                        # else just copy as is
                        else:
                            newcoords = copy.copy(coords)
                        # update coords
                        coords = copy.copy(newcoords)
                        coords[len(coords)-1] += 1

                        # reset paragraph counter, update bookmark
                        paraNum = 0
                        bookmark = w+1

#                # if it's not a section, but is the space just before a section, then we need to anticipate a section.
#                elif(ratio < lineratio):
#                    sectionwatch = True
#                    # Make all the sentences between bookmark and the end of the paragraph.
#                    sentlist = textprocessing.MakeSentences(makeString(
#                        words[bookmark:w+1]), coords, paraNum)
#
#                    # if this paragraph is split between 2 pages, then add these sentences to the first half of the paragraph.
#                    if(addto and len(activesection.para) > 0):
#                        addto = False
#                        activepara = activesection.para[len(
#                            activesection.para)-1]
#                        for s in range(len(sentlist)):
#                            if(s == 0):
#                                activepara.sentences[len(
#                                    activepara.sentences)-1].text += " " + sentlist[s].text
#                            else:
#                                activesection.para[len(
#                                    activesection.para)-1].sentences.append(sentlist[s])
#                    # If it's a normal paragraph, then add it to the list
#                    else:
#                        para = PDFfragments.paragraph(
#                            coords, paraNum, sentlist, copy.copy(cites))
#                        cites = []
#                        activesection.para.append(para)
#                        paraNum += 1
#                    bookmark = w+1
#                    sectionwatch = True

                # if it's the end of a non-section block, add that block as a paragraph.
                elif(end_block):
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
                # if it's just a newline, then we don't care.
                else:
                    if (textprocessing.DetermineParagraph(words, w, paraAlign, paraSpace, useSpace, ERROR_MARGIN)):
                        sentlist = textprocessing.MakeSentences(textprocessing.makeString(
                            words[bookmark:w+1]), copy.copy(coords), paraNum)
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
