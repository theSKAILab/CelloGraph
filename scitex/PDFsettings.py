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

        self.useSpace = False
        if(self.paraAlign == -1):
            self.useSpace = True

        self.newFig = False

        self.cites = []
        self.coords = [-1]
        self.addto = False
        self.consistentRatio = 0
        self.paraNum = 0
        self.bookmark = 0
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

        index = 0
        first1 = words[0]
        expect_num = False
        while first1["text"].isdigit():
            index += 1
            first1 = words[index]
        if words[index]["text"] == words2[index]["text"] and words2[index]["text"] == words3[index]["text"]:
            count = index
            for k in range(index, len(words)):
                if words[k]["text"] == words2[k]["text"] and words2[k]["text"] == words3[k]["text"]:
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
    return headers


def FindPageFooters(pdf, pdfSettings, hError):
    footers = []
    for i in range(len(pdf.pages)-4):
        words = PDFfunctions.getWords(pdf.pages[i], hError)
        visible1 = words[len(words)-250:]

        words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
        visible2 = words2[len(words2)-250:]

        words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)
        visible3 = words3[len(words3)-250:]

        index = 1
        first1 = words[len(words)-1]
        expect_num = False
        while first1["text"].isdigit():
            index += 1
            first1 = words[index]
        if words[len(words)-index]["text"] == words2[len(words2)-index]["text"] and words2[len(words2)-index]["text"] == words3[len(words3)-index]["text"]:
            count = 0
            for k in range(index+1, len(words)):
                if words[len(words)-k]["text"] == words2[len(words2)-k]["text"] and words2[len(words2)-k]["text"] == words3[len(words3)-k]["text"]:
                    count += 1
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
    return footers


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
