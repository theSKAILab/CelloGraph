from enum import Enum
import minorfunctions
import PDFfragments


class PDFsettings():
    def __init__(self, pdf, ERROR_MARGIN, PARAS_REQUIRED):
        self.paraAlign = -1
        self.paraSpace = -1

        self.linespace, self.lineratio, self.lineheight, self.paraAlign, self.paraSpace = FindSpace(
            pdf, ERROR_MARGIN, PARAS_REQUIRED)

        self.pageHeaders = FindPageHeaders(pdf)

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


def FindPageHeaders(pdf):
    headers = []
    for i in range(len(pdf.pages)):
        iwords = pdf.pages[i].extract_words(y_tolerance=6)
        for j in range(i+1, len(pdf.pages)):
            jwords = pdf.pages[j].extract_words(y_tolerance=6)
            if iwords[0] == jwords[0]:
                count = 1
                for k in range(1, len(iwords)):
                    if iwords[k] == jwords[k]:
                        count += 1
                    else:
                        break
                headers = minorfunctions.appendNoRepeats(
                    jwords[0:count], headers)
    return headers


# FindSpace: Takes a PDF and tries to figure out what the spacing is
# returns linespace, paraAlign, paraSpace
# linespace is the space between lines
# paraAlign is the left-margin on a standard line, so that any deviation can be
# detected as a new paragraph
# paraSpace is the vertical space between paragraphs, if that spacing is not the same as linespace.


def FindSpace(pdf, error, PARAS_REQUIRED):

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
    diffs = []

    for i in range(len(words)):
        bookmark = 0
        for j in range(1, len(words[i])):
            if(words[i][j-1]["top"] != words[i][j]["top"]):
                diff = words[i][j]["top"] - words[i][bookmark]["bottom"]
                height = words[i][j]["bottom"] - words[i][j]["top"]
                diffs.append({"AftSpace": float(diff), "LineEndDex": bookmark, "LineStartDex": j,
                             "Align": words[i][j]["x0"], "Height": height, "Ratio": float(height/diff)})
                bookmark = j

    # the most common difference is going to be the difference between one line and another.
    # True means we want an index and not the most common value.
    lineIndex = minorfunctions.mostCommonLineSpace(diffs, True, error)
    linespace = float(diffs[lineIndex]["AftSpace"])
    lineratio = float(diffs[lineIndex]["Ratio"])
    lineheight = float(diffs[lineIndex]["Height"])
    # paraAlign should be the x coordinate of the body text, so that any line with a different x-coordinate can be a new paragraph.

    paraSpace = -1
    paraAlign = -1
    paraCount = 0

    for d in range(1, len(diffs[0])-1):
        if(minorfunctions.listElementsEqual([diffs[d-1]["AftSpace"], linespace, diffs[d+1]["AftSpace"]], error) and isGreater(diffs[d]["AftSpace"], linespace, error)):
            paraSpace = diffs[d]["AftSpace"]
            paraCount = 0

    if(paraCount < PARAS_REQUIRED):
        paraSpace = -1

    if(paraSpace == -1):
        paraAlign = diffs[lineIndex]["Align"]

    return linespace, lineratio, lineheight, paraAlign, paraSpace
