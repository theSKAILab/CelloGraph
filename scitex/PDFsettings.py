from enum import Enum
import minorfunctions
import PDFfragments
import PDFfunctions
from minorfunctions import listElementsEqual
import textprocessing

# PDF Settings is a really big class that I use to hold onto a zillion different values while reading the PDF.

# paraAlign is the x-coordinate of a line of body text, so that any line that deviates from that can be suspected of being a new paragraph.
# paraSpace is used in the event that a PDF denotes paragraphs by vertical spacing instead of horizontal alignment.

# linespace, lineratio, and lineheight all describe features of normal body text lines.
# space is how much space is between lines.
# height is height of the line.
# ratio is the ratio between space and height.

# interline and intraline are vertical error values.
# horizontal is a horizontal error value.

# pageHeaders and pageFooters are arrays
# addto is whether the next paragraph needs to be stitched onto the previous one.
# addtoNext is whether the paragraph after next needs to be stitched onto the next one.

# consistentRatio is the lineratio between lines in a multiline header.
# offset is a measure of how many words have been removed from an array of words due to being figure text.


class PDFsettings():

    def __init__(self, pdf=None, vError=0, hError=0, PARAS_REQUIRED=0):
        self.paraAlign = -1
        self.paraSpace = -1

        if(pdf):
            self.linespace, self.lineratio, self.lineheight, self.paraAlign, self.paraSpace, self.interline, self.horizontal = FindSpace(
                pdf, vError, hError, PARAS_REQUIRED)

            self.intraline = self.linespace * .4

            self.pageHeaders = FindPageHeaders(pdf, self, hError)
            self.pageFooters = FindPageFooters(pdf, self, hError)

            self.pageHeaders = minorfunctions.sortByLen(self.pageHeaders)
            self.pageFooters = minorfunctions.sortByLen(self.pageFooters)

            self.useSpace = False
            if(self.paraAlign == -1):
                self.useSpace = True

        self.newFig = False

        self.cites = []
        self.coords = [0]
        self.addto = False
        self.addtoNext = False
        self.consistentRatio = 0
        self.paraNum = 0
        self.bookmark = 0
        self.offset = 0
        self.activesection = PDFfragments.section("")


# expect_num is whether the text right after the header is a page number.
class Header():
    def __init__(self, words, expect_num=False):
        self.words = words
        self.expect_num = expect_num

    def __eq__(self, other):
        return minorfunctions.reverseArr(self.words, "text") == minorfunctions.reverseArr(other.words, "text") and self.expect_num == self.expect_num


def FindPageHeaders(pdf, pdfSettings, hError):
    headers = []
    for i in range(len(pdf.pages)-4):
        words = PDFfunctions.getWords(pdf.pages[i], hError)
        words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
        words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)

        #get the header
        foundHeader = False
        headers, foundHeader = addHeader(headers, words, i, words2, words3)

        #if we didn't find a header, look backwards
        if(not foundHeader and i >= 4):
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    #look backwards for headers on the last 4 pages, since we can't look beyond the end of the doc.
    if(len(pdf.pages) > 4):
        for i in range(len(pdf.pages)-4, len(pdf.pages)):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    return headers



#adds the header in words to headers, if there is one.
#headers = a list of headers
#words = the page in question
#words2, words3 = two pages to compare words to when looking for headers.
#i the page number of words.
def addHeader(headers, words, i, words2, words3):
    visible1 = words[len(words)-240:]
    visible2 = words2[len(words2)-240:]
    visible3 = words3[len(words3)-240:]

    index = 0
    first1 = words[0]
    expect_num = False
    foundHeader = False
    if first1["text"].isdigit():
        if(int(first1) == first1["page"]):
            index += 1
    anyHeader = False
    x, offset = checkForHeaderOffset(words, words2, words3, index)
    if headerCheck(words, words2, words3, index, offset):
        anyHeader = True
    if anyHeader:
        oldOffset = offset
        foundHeader = True
        count = index
        k = index
        while k < len(words):
            k += 1
            if headerCheck(words, words2, words3, k, oldOffset):
                count += 1
                continue
            x, newOffset = checkForHeaderOffset(words, words2, words3, k)
            if(newOffset != 0 and newOffset != oldOffset):
                oldOffset = newOffset
                k -= x
            elif(words[len(words)-k]["text"].isdigit() and words[len(words)-k]["text"] == str(i+1)):
                expect_num = True
                break
            elif(words[len(words)-k]["text"][0:len(str(i+1))] == str(i+1) or words[len(words)-1]["text"][0:len(str(i+1))] == str(i+1)):
                expect_num = True
                break
            else:
                break
        text = words[index:count+1]
        headers = minorfunctions.appendNoRepeats(
            Header(text, expect_num), headers)
    return headers, foundHeader

# really long if statement, checks that words[index] is equal for all words or they're all numbers.
def headerCheck(words, words2, words3, index, offset=0):
    if(index < 0):
        index = 0
    w1 = words[index+offset]
    w2 = words2[index]
    w3 = words3[index]

    t1 = w1["text"]
    t2 = w2["text"]
    t3 = w3["text"]

    h1 = w1["bottom"] - w1["top"]
    h2 = w2["bottom"] - w2["top"]
    h3 = w3["bottom"] - w3["top"]

    if t1 == t2 and t2 == t3:
        if(minorfunctions.listElementsEqual([h1, h2, h3], 5, True)):
            return True

    t1 = textprocessing.trimScript(t1)
    t2 = textprocessing.trimScript(t2)
    t3 = textprocessing.trimScript(t3)

    if t1.isdigit() and t2.isdigit() and t3.isdigit():
        if(minorfunctions.listElementsEqual([int(t1), int(t2), int(t3)], 4)):
            if(minorfunctions.listElementsEqual([h1, h2, h3], 5, True)):
                return True

    return False


# returns true if w1, w2, w3 are all equal or all numbers within 4 of each other (for if they're page numbers)
def footerCheck(words, words2, words3, index, offset=0):
    if(index < 1):
        index = 1
    w1 = words[len(words)-index-offset]
    w2 = words2[len(words2)-index]
    w3 = words3[len(words3)-index]

    t1 = w1["text"]
    t2 = w2["text"]
    t3 = w3["text"]

    h1 = w1["bottom"] - w1["top"]
    h2 = w2["bottom"] - w2["top"]
    h3 = w3["bottom"] - w3["top"]

    if t1 == t2 and t2 == t3:
        if(minorfunctions.listElementsEqual([h1, h2, h3], 5, True)):
            return True

    t1 = textprocessing.trimScript(t1)
    t2 = textprocessing.trimScript(t2)
    t3 = textprocessing.trimScript(t3)

    if t1.isdigit() and t2.isdigit() and t3.isdigit():
        if(minorfunctions.listElementsEqual([int(t1), int(t2), int(t3)], 4)):
            if(minorfunctions.listElementsEqual([h1, h2, h3], 5, True)):
                return True

    return False


def FindPageFooters(pdf, pdfSettings, hError):
    footers = []
    for i in range(len(pdf.pages)-4):
        words = PDFfunctions.getWords(pdf.pages[i], hError)
        words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
        words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)

        visible1 = words[len(words)-240:]
        visible2 = words2[len(words2)-240:]
        visible3 = words3[len(words3)-240:]

        foundFooter = False
        footers, foundFooter = addFooter(footers, words, i, words2, words3)

        if(not foundFooter and i >= 4):
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            footers, foundFooter = addFooter(footers, words, i, words2, words3)

        if(not foundFooter and (i == 0 or i == 1)):
            words2 = PDFfunctions.getWords(pdf.pages[0], hError)
            words3 = PDFfunctions.getWords(pdf.pages[1], hError)
            footers, foundFooter = addFooter(footers, words, i, words2, words3)

    if(len(pdf.pages) > 4):
        for i in range(len(pdf.pages)-4, len(pdf.pages)):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)

            if(i-4 == 0 and len(pdf.pages) > i+2):
                words3 = PDFfunctions.getWords(pdf.pages[i+2], hError)

            visible1 = words[len(words)-240:]
            visible2 = words2[len(words2)-240:]
            visible3 = words3[len(words3)-240:]

            footers, foundFooter = addFooter(footers, words, i, words2, words3)

    return footers


def checkForFooterOffset(words, words2, words3, index):
    for x in range(10):
        for y in range(4):
            w1 = words[len(words)-index-y-x]["text"]
            w2 = words2[len(words2)-index-x]["text"]
            w3 = words3[len(words3)-index-x]["text"]
            if w1 == w2 and w2 == w3:
                if(x > 0):
                    x -= 1
                return x, y
            if w1.isdigit() and w2.isdigit() and w3.isdigit():
                num = int(w1)
                num2 = int(w2)
                num3 = int(w3)
                if(num2 == num + 2 and num3 == num2 + 2):
                    if(x > 0):
                        x -= 1
                    return x, y
    return 0, 0

def checkForHeaderOffset(words, words2, words3, index):
    for x in range(10):
        for y in range(4):
            w1 = words[index+y+x]["text"]
            w2 = words2[index+x]["text"]
            w3 = words3[index+x]["text"]
            if w1 == w2 and w2 == w3:
                if(x > 0):
                    x -= 1
                return x, y
            if w1.isdigit() and w2.isdigit() and w3.isdigit():
                num = int(w1)
                num2 = int(w2)
                num3 = int(w3)
                if(num2 == num + 2 and num3 == num2 + 2):
                    if(x > 0):
                        x -= 1
                    return x, y
    return 0, 0


def addFooter(footers, words, i, words2, words3):
    visible1 = words[len(words)-240:]
    visible2 = words2[len(words2)-240:]
    visible3 = words3[len(words3)-240:]

    index = 0
    first1 = words[len(words)-1]
    expect_num = False
    foundFooter = False
    if first1["text"].isdigit():
        if(int(first1["text"]) == first1["page"]):
            index += 1
    if footerCheck(words, words2, words3, index):
        foundFooter = True
        count = 0
        k = index
        oldOffset = 0
        while k < len(words):
            k += 1
            if footerCheck(words, words2, words3, k, oldOffset):
                count += 1
                continue
            x, newOffset = checkForFooterOffset(words, words2, words3, k)
            if(newOffset != 0 and newOffset != oldOffset):
                oldOffset = newOffset
                k -= x
            elif(words[len(words)-k]["text"].isdigit() and words[len(words)-k]["text"] == str(i+1)):
                expect_num = True
                break
            elif(words[len(words)-k]["text"][0:len(str(i+1))] == str(i+1) or words[len(words)-1]["text"][0:len(str(i+1))] == str(i+1)):
                expect_num = True
                break
            else:
                break
        text = words[len(words)-count-1:len(words)-index+1]
        footers = minorfunctions.appendNoRepeats(
            Header(text, expect_num), footers)
    return footers, foundFooter


# FindSpace: Takes a PDF and tries to figure out what the spacing is
# returns linespace, paraAlign, paraSpace
# linespace is the space between lines
# paraAlign is the left-margin on a standard line, so that any deviation can be
# detected as a new paragraph
# paraSpace is the vertical space between paragraphs, if that spacing is not the same as linespace.

def FindSpace(pdf, vError, hError, PARAS_REQUIRED):
    tempSettings = PDFsettings()

    # For now we're going to use the first three pages, because if there are 3 pages without a
    # normal line space; paragraph space; and a section space, then too bad. (for now)
    pages = []
    pages.append(PDFfunctions.getWords(pdf.pages[0], hError))
    if(len(pdf.pages) > 1):
        pages.append(PDFfunctions.getWords(pdf.pages[1], hError))
    if(len(pdf.pages) > 2):
        pages.append(PDFfunctions.getWords(pdf.pages[2], hError))

    # for each word, if it has a different y coordinate, note the difference

    lines = []
    spaces = []

    for i in range(len(pages)): 
        words = pages[i]
        words, pLine, pSpace = PDFfunctions.getLines(words, tempSettings, vError, True)
        lines += pLine
        spaces += pSpace

    # the most common difference is going to be the difference between one line and another.
    # True means we want an index and not the most common value.
    spaceIndex = minorfunctions.mostCommonLineSpace(lines, True, vError/100)
    linespace = float(lines[spaceIndex]["AftSpace"])
    heightIndex = minorfunctions.mostCommonLineHeight(lines, True, vError/100)
    lineratio = float(lines[heightIndex]["AftRatio"])
    lineheight = float(lines[heightIndex]["Height"])

    wordspace = float(minorfunctions.mostCommon(spaces, False, hError))
    vert = linespace * ((vError)/100)
    horizontal = wordspace * ((hError)/100)

    # paraAlign should be the x coordinate of the body text, so that any line with a different x-coordinate can be a new paragraph.

    paraSpace = -1
    paraAlign = -1
    paraCount = 0

    for i in range(1, len(lines)-1):
        if(minorfunctions.listElementsEqual([lines[i-1]["AftSpace"], linespace, lines[i+1]["AftSpace"]], vError) and minorfunctions.isGreater(lines[i]["AftSpace"], linespace, vError)):
            paraSpace = lines[i]["AftSpace"]
            paraCount = 0

    if(paraCount < PARAS_REQUIRED):
        paraSpace = -1

    if(paraSpace == -1):
        paraAlign = lines[heightIndex]["Align"]

    return linespace, lineratio, lineheight, paraAlign, paraSpace, vert, horizontal



def newSpacing(lines, page, pdfSettings):
    if(len(lines) < 1):
        return pdfSettings

    vError = pdfSettings.interline
    hError = pdfSettings.horizontal

    spaceIndex = minorfunctions.mostCommonLineSpace(lines, True, vError/100)
    linespace = float(lines[spaceIndex]["AftSpace"])
    heightIndex = minorfunctions.mostCommonLineHeight(lines, True, vError/100)
    lineratio = float(lines[heightIndex]["AftRatio"])
    lineheight = float(lines[heightIndex]["Height"])

    pdfSettings.linespace = linespace
    pdfSettings.lineheight = lineheight
    pdfSettings.lineratio = lineratio

    if(page == 1):
        pdfSettings.interline = linespace * .7
    else:
        pdfSettings.interline = pdfSettings.intraline / .4

    return pdfSettings