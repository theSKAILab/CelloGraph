from enum import Enum
import minorfunctions
import PDFfragments


class PDFsettings():
    def __init__(self, pdf, vError, hError, PARAS_REQUIRED):
        self.paraAlign = -1
        self.paraSpace = -1

        self.linespace, self.lineratio, self.lineheight, self.paraAlign, self.paraSpace, self.vert, self.horizontal = FindSpace(
            pdf, vError, hError, PARAS_REQUIRED)

        self.pageHeaders = FindPageHeaders(pdf, self)
        self.pageFooters = FindPageFooters(pdf, self)

        self.useSpace = False
        if(self.paraAlign == -1):
            self.useSpace = True

        self.cites = []
        self.coords = [-1]
        self.addto = False
        self.consistentRatio = 0
        self.paraNum = 0
        self.bookmark = 0
        self.activesection = PDFfragments.section("")


def FindPageHeaders(pdf, pdfSettings):
    headers = []
    for i in range(len(pdf.pages)-4):
        words = pdf.pages[i].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        words2 = pdf.pages[i+2].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        words3 = pdf.pages[i+4].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        index = 0
        first1 = words[0]
        while first1["text"].isdigit():
            index += 1
            first1 = words[index]
        if words[index]["text"] == words2[index]["text"] and words2[index]["text"] == words3[index]["text"]:
            count = 1
            for k in range(index, len(words)):
                if words[k]["text"] == words2[k]["text"] and words2[k]["text"] == words3[k]["text"]:
                    count += 1
                else:
                    break
            headers = minorfunctions.appendNoRepeats(
                words[0:count], headers)
    return headers


def FindPageFooters(pdf, pdfSettings):
    headers = []
    for i in range(len(pdf.pages)-4):
        words = pdf.pages[i].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        words2 = pdf.pages[i+2].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        words3 = pdf.pages[i+4].extract_words(
            y_tolerance=pdfSettings.vert, x_tolerance=pdfSettings.horizontal)
        if words[len(words)-1] == words2[len(words2)-1] and words2[len(words2)-1] == words3[len(words3)-1]:
            count = 1
            for k in range(1, len(words)):
                if words[len(words)-k] == words2[len(words2)-k] and words2[len(words2)-k] == words3[len(words2)-k]:
                    count += 1
                else:
                    break
            headers = minorfunctions.appendNoRepeats(
                words[len(words)-count: len(words)], headers)
    return headers


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
    pages.append(pdf.pages[0].extract_words(y_tolerance=1, x_tolerance=1))
    pages.append(pdf.pages[1].extract_words(y_tolerance=1, x_tolerance=1))
    pages.append(pdf.pages[2].extract_words(y_tolerance=1, x_tolerance=1))

    # for each word, if it has a different y coordinate, note the difference
    # diffs[0] is the distance between lines
    # diffs[1] is the index of the last word of the previous line
    # diffs[2] is the first index of each line
    # diffs[3] is the left-alignment of the first word of each line
    # diffs[4] is, for each line, the height of that line divided by the space between that line and the next line.
    # diffs[5] is the height of each line
    diffs = []
    spaces = []

    for i in range(len(pages)):
        bookmark = 0
        words = pages[i]
        for j in range(1, len(words)):
            if(not minorfunctions.areEqual(words[j-1]["top"], words[j]["top"], vError)):
                diff = words[j]["top"] - words[bookmark]["bottom"]
                height = words[j]["bottom"] - words[j]["top"]
                diffs.append({"AftSpace": float(diff), "LineEndDex": bookmark, "LineStartDex": j,
                             "Align": words[j]["x0"], "Height": height, "Ratio": float(height/diff)})
                bookmark = j
            else:
                spaces.append(words[j]["x0"]-words[j-1]["x1"])

    # the most common difference is going to be the difference between one line and another.
    # True means we want an index and not the most common value.
    lineIndex = minorfunctions.mostCommonLineSpace(diffs, True, vError)
    linespace = float(diffs[lineIndex]["AftSpace"])

    wordspace = float(minorfunctions.mostCommon(spaces, False, hError))
    vert = linespace * ((100-vError)/100)
    horizontal = wordspace * ((100-hError)/100)
    lineratio = float(diffs[lineIndex]["Ratio"])
    lineheight = float(diffs[lineIndex]["Height"])
    # paraAlign should be the x coordinate of the body text, so that any line with a different x-coordinate can be a new paragraph.

    paraSpace = -1
    paraAlign = -1
    paraCount = 0

    for d in range(1, len(diffs[0])-1):
        if(minorfunctions.listElementsEqual([diffs[d-1]["AftSpace"], linespace, diffs[d+1]["AftSpace"]], vError) and isGreater(diffs[d]["AftSpace"], linespace, vError)):
            paraSpace = diffs[d]["AftSpace"]
            paraCount = 0

    if(paraCount < PARAS_REQUIRED):
        paraSpace = -1

    if(paraSpace == -1):
        paraAlign = diffs[lineIndex]["Align"]

    return linespace, lineratio, lineheight, paraAlign, paraSpace, vert, horizontal
