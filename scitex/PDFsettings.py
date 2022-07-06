from enum import Enum
import minorfunctions
import PDFfragments
import PDFfunctions
import textprocessing


class PDFsettings():
    def __init__(self, pdf, vError, hError, PARAS_REQUIRED):
        self.paraAlign = -1
        self.paraSpace = -1

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
        self.coords = [-1]
        self.addto = False
        self.addtoNext = False
        self.consistentRatio = 0
        self.paraNum = 0
        self.bookmark = 0
        self.offset = 0
        self.activesection = PDFfragments.section("")


class Header():
    def __init__(self, text, expect_num=False):
        self.text = text
        self.expect_num = expect_num

    def __eq__(self, other):
        return minorfunctions.reverseArr(self.text, "text") == minorfunctions.reverseArr(other.text, "text") and self.expect_num == self.expect_num


def FindPageHeaders(pdf, pdfSettings, hError):
    headers = []
    for i in range(len(pdf.pages)-4):
        words = PDFfunctions.getWords(pdf.pages[i], hError)
        words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
        words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)

        foundHeader = False
        headers, foundHeader = addHeader(headers, words, i, words2, words3)

        if(not foundHeader and i >= 4):
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    if(len(pdf.pages) > 4):
        for i in range(len(pdf.pages)-4, len(pdf.pages)):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    return headers


def addHeader(headers, words, i, words2, words3):
    index = 0
    first1 = words[0]
    expect_num = False
    foundHeader = False
    while first1["text"].isdigit():
        index += 1
        first1 = words[index]
    if(headerCheck(words, words2, words3, index)):
        foundHeader = True
        count = index
        for k in range(index, len(words)):
            if headerCheck(words, words2, words3, k):
                count += 1
            elif(words[k]["text"].isdigit() and words[k]["text"] == i+1):
                expect_num = True
                break
            elif(words[k]["text"][0:len(str(i+1))] == str(i+1)):
                expect_num = True
                break
            else:
                break
        headers = minorfunctions.appendNoRepeats(
            Header(words[index:count], expect_num), headers)
    return headers, foundHeader


# really long if statement, checks that words[index] is equal for all words or they're all numbers.
def headerCheck(words, words2, words3, index, offset=0):
    if(index < 0):
        index = 0
    w1 = words[index+offset]["text"]
    w2 = words2[index]["text"]
    w3 = words3[index]["text"]

    if w1 == w2 and w2 == w3:
        return True

    w1 = textprocessing.trimScript(w1)
    w2 = textprocessing.trimScript(w2)
    w3 = textprocessing.trimScript(w3)

    if w1.isdigit() and w2.isdigit() and w3.isdigit():
        num = int(w1)
        num2 = int(w2)
        num3 = int(w3)
        if(minorfunctions.listElementsEqual([int(w1), int(w2), int(w3)], 4)):
            return True

    return False


# returns true if w1, w2, w3 are all equal or all numbers within 4 of each other (for if they're page numbers)
def footerCheck(words, words2, words3, index, offset=0):
    if(index < 1):
        index = 1
    w1 = words[len(words)-index-offset]["text"]
    w2 = words2[len(words2)-index]["text"]
    w3 = words3[len(words3)-index]["text"]

    if w1 == w2 and w2 == w3:
        return True

    w1 = textprocessing.trimScript(w1)
    w2 = textprocessing.trimScript(w2)
    w3 = textprocessing.trimScript(w3)
    if w1.isdigit() and w2.isdigit() and w3.isdigit():
        num = int(w1)
        num2 = int(w2)
        num3 = int(w3)
        if(minorfunctions.listElementsEqual([int(w1), int(w2), int(w3)], 4)):
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


def checkForOffset(words, words2, words3, index):
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


def addFooter(footers, words, i, words2, words3):
    visible1 = words[len(words)-240:]
    visible2 = words2[len(words2)-240:]
    visible3 = words3[len(words3)-240:]

    index = 1
    first1 = words[len(words)-1]
    expect_num = False
    foundFooter = False
    if first1["text"].isdigit():
        if(int(first1["text"]) == first1["Page"]):
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
            x, newOffset = checkForOffset(words, words2, words3, k)
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
        bookmark = 0
        words = pages[i]
        for j in range(1, len(words)):
            if(textprocessing.newline(words, j, vError/10)):
                diff = words[j]["top"] - words[bookmark]["bottom"]
                height = words[j]["bottom"] - words[j]["top"]
                lines.append({"AftSpace": float(diff), "LineEndDex": bookmark, "LineStartDex": j,
                             "Align": words[j]["x0"], "Height": height, "Ratio": float(height/diff), "Text": words[bookmark:j]})
                bookmark = j
            else:
                spaces.append(words[j]["x0"]-words[j-1]["x1"])

    # the most common difference is going to be the difference between one line and another.
    # True means we want an index and not the most common value.
    lineIndex = minorfunctions.mostCommonLineSpace(lines, True, vError/100)
    linespace = float(lines[lineIndex]["AftSpace"])
    lineratio = float(lines[lineIndex]["Ratio"])
    lineheight = float(lines[lineIndex]["Height"])

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
        paraAlign = lines[lineIndex]["Align"]

    return linespace, lineratio, lineheight, paraAlign, paraSpace, vert, horizontal
