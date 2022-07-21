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
import PDFsettings
import PDFfunctions
import time

# This is a document containing all the major functions that get used in the code

# higher number = more precise
VERTICAL_ERROR = 5
HORIZONTAL_ERROR = 30

#I'm not sure this actually gets used. I'll check later and if it doesn't, I'll remove it.
RATIO_MARGIN = 0.05

# PARAS_REQUIRED is the number of unusual spaces that have to happen before I'll believe that they're being used
# to determine different paragraphs.
PARAS_REQUIRED = 2

# PDFSort: Takes a pdf from pdfplumber, a PDF class from above, and two numbers to calibrate reading.


def PDFSort(pdf, times=False):

    # declare variables that get used later.
    PDF = PDFfragments.PDFdocument()
    timeArr = []

    #Initialize pdfSettings and measure how long it takes.
    sec1 = time.time()
    pdfSettings = PDFsettings.PDFsettings(
        pdf, VERTICAL_ERROR, HORIZONTAL_ERROR, PARAS_REQUIRED)
    sec2 = time.time()
    print("Time to initialize PDFsettings: " + str(sec2-sec1))

    #Deal with each page, and measure how long it takes to do that.
    for pg in range(len(pdf.pages)):
        sec1 = time.time()
        PDF, pdfSettings = DealWithPage(PDF, pdf.pages[pg], pdfSettings)
        sec2 = time.time()

        print("Time to Deal With Page " +
              str(pg) + ": " + str(sec2 - sec1))
        timeArr.append(sec2-sec1)

    # do some cleaning up.
    for i in range(len(PDF.sections)):
        PDF.sections[i] = PDFfunctions.cleanSection(PDF.sections[i])

    # PDF = PDFfunctions.removeBibliography

    #return the PDF.
    if(times):
        return PDF, timeArr
    else:
        return PDF


def DealWithPage(PDF, page, pdfSettings):

    if(page.page_number == 3):
        print("Breakpoint")

    #get the array of characters from pdfPlumber.
    pagechars = page.chars


    #organize the characters into words and measure how long it takes.
    sec3 = time.time()
    pagewords = PDFfunctions.getWords(page, HORIZONTAL_ERROR)
    sec4 = time.time()
    print("Time to get words: " + str(sec4 - sec3))

    #get rid of any headers / footers.
    if(len(pdfSettings.pageHeaders) > 0):
        pagewords = PDFfunctions.removePageHeadersEarly(
            pagewords, page.page_number, pdfSettings)
    if(len(pdfSettings.pageFooters) > 0):
        pagewords = PDFfunctions.removePageFootersEarly(
            pagewords, page.page_number, pdfSettings)

    ## get rid of any tables. 
    #if(page.page_number != 1):
    #    PDF, words = PDFfunctions.removeTables(
    #        PDF, pdfSettings, page, pagewords)


    #organize the words into columns.
    cols = textprocessing.HandleColumns(
        pagewords, pdfSettings.horizontal, pdfSettings.intraline)

    
    #deal with each column.
    for c in range(len(cols)):
        pdfSettings.bookmark = 0
        PDF, pdfSettings = DealWithCol(PDF, page, c, cols[c], pdfSettings)

    #return the PDF.
    return PDF, pdfSettings


def DealWithCol(PDF, page, colnum, words, pdfSettings):

    pdfSettings.offset = 0

    #organize the words into lines.
    words, lines, pdfSettings = PDFfunctions.getLines(
        words, pdfSettings, pdfSettings.intraline)

    #deal with each line.
    #IT IS IMPORTANT THAT THIS IS A WHILE AND NOT A FOR LOOP.
    #a while loop lets me edit the number of lines while we're inside the loop.
    i = -1
    while i < len(lines)-1:
        i += 1
        PDF, pdfSettings, lines, i = DealWithLine(
            PDF, words, lines, i, pdfSettings, page.page_number, colnum)

    # Add whatever text is at the end of the col.
    if(pdfSettings.bookmark < len(words)-1):
        w = len(words)-1
        pdfSettings = PDFfunctions.extensiveAddPara(
            pdfSettings, words, w, page.page_number, colnum)

    #return the PDF and the updated settings.
    return PDF, pdfSettings


def DealWithLine(PDF, words, lines, lineIndex, pdfSettings, pagenum, colnum):

    if(lineIndex == 26):
        print("Breakpoint")

    sec1 = time.time()

    w = lines[lineIndex]["LineEndDex"]-pdfSettings.offset
    if(w > len(words)-1):
        w = len(words)-1

    #Figure out what kind of line this is.
    settings = textSettings.lineSettings(
        lineIndex, lines, pdfSettings, pdfSettings.interline)

    #Deal with it appropriately.

    #If we're in a multi-line header, we're good.
    if(settings.type == textSettings.lineType.IN_MULTI):
        return PDF, pdfSettings, lines, lineIndex

    #If this is the beginning of a multiline header, mark the ratio between line height and line spacing.
    elif(settings.type == textSettings.lineType.START_MULTI):
        pdfSettings.consistentRatio = lines[lineIndex]["AftRatio"]

    #If this is the end of a section header / a one-line section header, add it.
    elif(settings.type == textSettings.lineType.END_SECTION):
        if(pdfSettings.bookmark < len(words)):
            PDF, pdfSettings, lines = PDFfunctions.registerSection(
                PDF, words, w, lines, lineIndex, pdfSettings, pagenum, colnum)

    # if it's the end of a non-section block, add that block as a paragraph.
    # Most often this occurs just before a section header.
    elif(settings.type == textSettings.lineType.END_BLOCK):
        pdfSettings = PDFfunctions.extensiveAddPara(
            pdfSettings, words, w, pagenum, colnum)

    # if we find a figure header, add that.
    elif(settings.type == textSettings.lineType.FIGURE_TEXT):
        # add figure, ignore this line
        PDF, pdfSettings, lines, words = PDFfunctions.registerFigure(
            PDF, lines, lineIndex, words, pdfSettings, pagenum, colnum)
        lineIndex -= 1

    # if there's a new paragraph, add that.
    elif (textprocessing.DetermineParagraph(lines, lineIndex, pdfSettings, pdfSettings.interline)):
        pdfSettings.consistentRatio = 0
        pdfSettings = PDFfunctions.extensiveAddPara(
            pdfSettings, words, lines[lineIndex]["LineStartDex"]-1-(pdfSettings.offset), pagenum, colnum)

    sec2 = time.time()

    print("Time to Deal With Line " + str(lineIndex) + ": " + str(sec2 - sec1))

    return PDF, pdfSettings, lines, lineIndex
