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

# This is a document containing all the functions that get used in the code

# mostly cuz I don't wanna look through 5000 lines when I'm looking at code.py

# these are sorta misnomers but the higher these values are the lower the actual error value will be
VERTICAL_ERROR = 5
HORIZONTAL_ERROR = 10
RATIO_MARGIN = 0.05

# para-margin is the number of unusual spaces that have to happen before I'll believe that they're being used
# to determine different paragraphs.
PARAS_REQUIRED = 2

# PDFSort: Takes a pdf from pdfplumber, a PDF class from above, and two numbers to calibrate reading.


def PDFSort(pdf):

    # declare variables that get used later.
    PDF = PDFfragments.PDFdocument()

    pdfSettings = PDFsettings.PDFsettings(
        pdf, VERTICAL_ERROR, HORIZONTAL_ERROR, PARAS_REQUIRED)

    for pg in range(len(pdf.pages)):
        PDF, pdfSettings = DealWithPage(PDF, pdf.pages[pg], pdfSettings)

    # PDF = PDFfunctions.removeBibliography
    # bib must be removed before page/fig headers so that bib info don't get deleted
    #PDF = PDFfunctions.removePageHeaderSentences(PDF)

    #PDF = PDFfunctions.removeFigureHeaders(PDF)

    return PDF


def DealWithPage(PDF, page, pdfSettings):

    if(page.page_number == 30):
        print("Breakpoint")

    pagechars = page.chars

    pagewords = PDFfunctions.getWords(page, HORIZONTAL_ERROR)
    pagewords = PDFfunctions.removePageHeadersEarly(
        pagewords, page.page_number, pdfSettings)

    hate = pagewords[len(pagewords)-300:]

    # cols = textprocessing.HandleColumns(
    #    pagewords, pdfSettings.horizontal, pdfSettings.intraline)

    cols = [pagewords]

    for c in range(len(cols)):
        pdfSettings.bookmark = 0
        PDF, pdfSettings = DealWithCol(PDF, page, cols[c], pdfSettings)

    return PDF, pdfSettings


def DealWithCol(PDF, page, words, pdfSettings):
    PDF, words = PDFfunctions.removeTables(
        PDF, page, words, pdfSettings.interline)

    lines, pdfSettings = PDFfunctions.getLines(
        words, pdfSettings, pdfSettings.intraline)

    for i in range(len(lines)):
        PDF, pdfSettings = DealWithLine(
            PDF, words, lines, i, pdfSettings, page.page_number)

    # Add whatever text is at the end of the col.
    if(pdfSettings.bookmark != len(words)-1):
        w = len(words)-1

        sentlist = textprocessing.MakeSentences(textprocessing.makeString(
            words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)
        if(len(sentlist) == 0):
            return PDF, pdfSettings
        elif(pdfSettings.addto):
            addto = False
            if(len(pdfSettings.activesection.para) == 0):
                newpara = PDFfragments.paragraph(
                    pdfSettings.coords, pdfSettings.paraNum)
                pdfSettings.activesection.para.append(newpara)
            activepara = pdfSettings.activesection.para[len(
                pdfSettings.activesection.para)-1]
            for s in range(len(sentlist)):
                if(s == 0):
                    if(len(activepara.sentences) > 0):
                        activepara.sentences[len(
                            activepara.sentences)-1].text += " " + sentlist[s].text
                    else:
                        activepara.sentences.append(" " + sentlist[s].text)
                else:
                    pdfSettings.activesection.para[len(
                        pdfSettings.activesection.para)-1].sentences.append(sentlist[s])
        else:
            para = PDFfragments.paragraph(
                pdfSettings.coords, pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites))
            pdfSettings.activesection.para.append(para)
            pdfSettings.paraNum += 1
        pdfSettings.bookmark = 0

    return PDF, pdfSettings


def DealWithLine(PDF, words, lines, lineIndex, pdfSettings, pagenum):
    w = lines[lineIndex]["LineEndDex"]
    if(w > len(words)-1):
        w = len(words)-1

    if(lineIndex == 18):
        print("Breakpoint")

    settings = textSettings.lineSettings(
        lineIndex, lines, pdfSettings, pdfSettings.interline)

    if(settings.type == textSettings.lineType.START_MULTI):
        pdfSettings.consistentRatio = lines[lineIndex]["AftRatio"]

    elif(settings.type == textSettings.lineType.END_SECTION):
        pdfSettings.addto = False
        pdfSettings.consistentRatio = 0
        if(pdfSettings.bookmark < len(words)):
            type = textprocessing.FindsectionType(
                words[pdfSettings.bookmark], pdfSettings.activesection, pagenum, lines[lineIndex]["Height"], pdfSettings.intraline)

            if(len(lines[lineIndex]["Text"]) < 2 and len(lines[lineIndex]["Text"][0]["text"]) < 3):
                type = pdfSettings.activesection.type+1

            pdfSettings.coords = minorfunctions.newCoords(
                pdfSettings.coords, type)

            PDF, pdfSettings.activesection = PDFfunctions.addSection(pdfSettings.activesection,
                                                                     textprocessing.makeString(words[pdfSettings.bookmark:w+1]), type, PDF, pdfSettings, lines[lineIndex]["Height"], pagenum, pdfSettings.intraline)

            pdfSettings.activesection = minorfunctions.updateActiveSection(
                PDF, words, pdfSettings)

            pdfSettings.paraNum = 0
            pdfSettings.bookmark = w+1

    # if it's the end of a non-section block, add that block as a paragraph.
    elif(settings.type == textSettings.lineType.END_BLOCK):
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
    # if there's a new paragraph, add that.
    elif (textprocessing.DetermineParagraph(words, w, pdfSettings, pdfSettings.interline)):
        sentlist = textprocessing.MakeSentences(textprocessing.makeString(
            words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)
        # if this is the 2nd half of a cutoff paragraph, sew it back together.
        if(pdfSettings.addto and len(pdfSettings.activesection.para) > 0):
            pdfSettings.addto = False
            activepara = pdfSettings.activesection.para[len(
                pdfSettings.activesection.para)-1]
            while(len(activepara.sentences) == 0):
                pdfSettings.activesection.para.pop(len(
                    pdfSettings.activesection.para)-1)
                activepara = pdfSettings.activesection.para[len(
                    pdfSettings.activesection.para)-1]
            for s in range(len(sentlist)):
                if(s == 0):
                    activepara.sentences[len(
                        activepara.sentences)-1].text += " " + sentlist[s].text
                else:
                    pdfSettings.activesection.para[len(
                        pdfSettings.activesection.para)-1].sentences.append(sentlist[s])
        else:
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

    return PDF, pdfSettings
