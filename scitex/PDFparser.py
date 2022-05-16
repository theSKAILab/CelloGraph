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

# Sometimes the lines are just a little bit off in terms of how far away they are. I.e. two lines will be 13.7 apart, the next two will be 14.1
VERTICAL_ERROR = .7
HORIZONTAL_ERROR = 4
RATIO_MARGIN = 0.05

# para-margin is the number of unusual spaces that have to happen before I'll believe that they're being used
# to determine different paragraphs.
PARAS_REQUIRED = 2


# PDFSort: Takes a pdf from pdfplumber, a PDF class from above, and two numbers to calibrate reading.
def PDFSort(pdf):

    # declare variables that get used later.
    PDF = PDFfragments.PDFdocument()

    pdfSettings = PDFsettings.PDFsettings(pdf, VERTICAL_ERROR, PARAS_REQUIRED)

    for pg in range(len(pdf.pages)):
        PDF, pdfSettings = DealWithPage(PDF, pdf.pages[pg], pdfSettings)

    #PDF = PDFfunctions.removeBibliography
    # bib must be removed before page/fig headers so that bib info don't get deleted
    PDF = PDFfunctions.removePageHeaderSentences(PDF)
    #PDF = PDFfunctions.removePageHeaders(PDF)
    # PDFfunctions.removeFigureHeaders(PDF)

    return PDF


def DealWithPage(PDF, page, pdfSettings):
    pagewords = (page.extract_words(y_tolerance=6))
    cols = textprocessing.HandleColumns(pagewords, HORIZONTAL_ERROR)
    for c in range(len(cols)):
        pdfSettings.bookmark = 0
        PDF, pdfSettings = DealWithCol(PDF, cols[c], pdfSettings)

    return PDF, pdfSettings


def DealWithCol(PDF, words, pdfSettings):
    diffs, pdfSettings = PDFfunctions.getDiffs(
        words, pdfSettings, VERTICAL_ERROR)

    for d in range(len(diffs)):
        PDF, pdfSettings = DealWithDiff(
            PDF, words, diffs, d, pdfSettings)

    # Add whatever text is at the end of the col.
    if(pdfSettings.bookmark != len(words)-1):
        w = diffs[len(diffs)-1]["LineEndDex"]
        if(w > len(words)-1):
            w = len(words)-1
        sentlist = textprocessing.MakeSentences(textprocessing.makeString(
            words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)
        if(pdfSettings.addto):
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
                        activesection.para)-1].sentences.append(sentlist[s])
        else:
            para = PDFfragments.paragraph(
                pdfSettings.coords, pdfSettings.paraNum, sentlist, copy.copy(pdfSettings.cites))
            pdfSettings.activesection.para.append(para)
            pdfSettings.paraNum += 1
        pdfSettings.bookmark = 0

    return PDF, pdfSettings


def DealWithDiff(PDF, words, diffs, d, pdfSettings):
    w = diffs[d]["LineEndDex"]
    if(d == 32):
        endofline = words[w]
        newline = words[w+1]
        print("Breakpoint")
    if(w > len(words)-1):
        w = len(words)-1

    settings = textSettings.diffSettings(
        d, diffs, pdfSettings, VERTICAL_ERROR)

    if(settings.type == textSettings.diffType.START_MULTI):
        pdfSettings.consistentRatio = diffs[d]["AftRatio"]

    elif(settings.type == textSettings.diffType.END_SECTION):
        pdfSettings.addto = False
        pdfSettings.consistentRatio = 0
        if(pdfSettings.bookmark < len(words)):
            type = textprocessing.FindsectionType(words[pdfSettings.bookmark])

            PDFfunctions.addSection(pdfSettings.activesection,
                                    textprocessing.makeString(words[pdfSettings.bookmark:w+1]), type, PDF)

            pdfSettings.activesection = minorfunctions.updateActiveSection(
                PDF, words, pdfSettings)

            pdfSettings.coords = minorfunctions.newCoords(
                pdfSettings.coords, type)

            pdfSettings.paraNum = 0
            pdfSettings.bookmark = w+1

    # if it's the end of a non-section block, add that block as a paragraph.
    elif(settings.type == textSettings.diffType.END_BLOCK):
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
    elif (textprocessing.DetermineParagraph(words, w, pdfSettings, VERTICAL_ERROR)):
        sentlist = textprocessing.MakeSentences(textprocessing.makeString(
            words[pdfSettings.bookmark:w+1]), copy.copy(pdfSettings.coords), pdfSettings.paraNum)
        # if this is the 2nd half of a cutoff paragraph, sew it back together.
        if(pdfSettings.addto):
            pdfSettings.addto = False
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
