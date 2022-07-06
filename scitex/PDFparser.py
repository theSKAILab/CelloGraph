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

# This is a document containing all the functions that get used in the code

# mostly cuz I don't wanna look through 5000 lines when I'm looking at code.py

# higher number = more precise
VERTICAL_ERROR = 5
HORIZONTAL_ERROR = 30
RATIO_MARGIN = 0.05

# para-margin is the number of unusual spaces that have to happen before I'll believe that they're being used
# to determine different paragraphs.
PARAS_REQUIRED = 2

# PDFSort: Takes a pdf from pdfplumber, a PDF class from above, and two numbers to calibrate reading.


def PDFSort(pdf, times=False):

    # declare variables that get used later.
    PDF = PDFfragments.PDFdocument()
    timeArr = []

    sec1 = time.time()
    pdfSettings = PDFsettings.PDFsettings(
        pdf, VERTICAL_ERROR, HORIZONTAL_ERROR, PARAS_REQUIRED)
    sec2 = time.time()
    print("Time to initialize PDFsettings: " + str(sec2-sec1))

    for pg in range(len(pdf.pages)):
        sec1 = time.time()
        PDF, pdfSettings = DealWithPage(PDF, pdf.pages[pg], pdfSettings)
        sec2 = time.time()

        print("Time to Deal With Page " +
              str(pg) + ": " + str(sec2 - sec1))
        timeArr.append(sec2-sec1)

    for i in range(len(PDF.sections)):
        PDF.sections[i] = PDFfunctions.cleanSection(PDF.sections[i])

    # PDF = PDFfunctions.removeBibliography
    # bib must be removed before page/fig headers so that bib info don't get deleted
    # PDF = PDFfunctions.removePageHeaderSentences(PDF)

    # PDF = PDFfunctions.removeFigureHeaders(PDF)

    if(times):
        return PDF, timeArr
    else:
        return PDF


def DealWithPage(PDF, page, pdfSettings):

    if(page.page_number == 6):
        print("Breakpoint")

    pagechars = page.chars

    sec3 = time.time()
    pagewords = PDFfunctions.getWords(page, HORIZONTAL_ERROR)
    sec4 = time.time()
    print("Time to get words: " + str(sec4 - sec3))
    if(len(pdfSettings.pageHeaders) > 0):
        pagewords = PDFfunctions.removePageHeadersEarly(
            pagewords, page.page_number, pdfSettings)
    if(len(pdfSettings.pageFooters) > 0):
        pagewords = PDFfunctions.removePageFootersEarly(
            pagewords, page.page_number, pdfSettings)

    hate = pagewords[len(pagewords)-300:]

    cols = textprocessing.HandleColumns(
        pagewords, pdfSettings.horizontal, pdfSettings.intraline)

    # cols = [pagewords]

    for c in range(len(cols)):
        pdfSettings.bookmark = 0
        PDF, pdfSettings = DealWithCol(PDF, page, c, cols[c], pdfSettings)

    return PDF, pdfSettings


def DealWithCol(PDF, page, colnum, words, pdfSettings):

    pdfSettings.offset = 0

    PDF, words = PDFfunctions.removeTables(
        PDF, page, words, pdfSettings.interline)

    words, lines, pdfSettings = PDFfunctions.getLines(
        words, pdfSettings, pdfSettings.intraline)

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

    return PDF, pdfSettings


def DealWithLine(PDF, words, lines, lineIndex, pdfSettings, pagenum, colnum):

    if(lineIndex == 4):
        print("Breakpoint")

    sec1 = time.time()

    w = lines[lineIndex]["LineEndDex"]-pdfSettings.offset
    if(w > len(words)-1):
        w = len(words)-1

    settings = textSettings.lineSettings(
        lineIndex, lines, pdfSettings, pdfSettings.interline)

    if(settings.type == textSettings.lineType.IN_MULTI):
        return PDF, pdfSettings, lines, lineIndex

    if(settings.type == textSettings.lineType.START_MULTI):
        pdfSettings.consistentRatio = lines[lineIndex]["AftRatio"]

    elif(settings.type == textSettings.lineType.END_SECTION):
        if(pdfSettings.bookmark < len(words)):
            PDF, pdfSettings, lines = PDFfunctions.registerSection(
                PDF, words, w, lines, lineIndex, pdfSettings, pagenum, colnum)

    # if it's the end of a non-section block, add that block as a paragraph.
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
