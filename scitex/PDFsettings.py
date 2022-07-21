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
            #linespace is the space between two lines of body text.
            #lineratio is the ratio between linespace and lineheight.
            #lineheight is the height of a line of body text.
            #self.paraAlign is the x0 coordinate of a normal line of body text. Paragraph indents will deviate from this number.
            #self.interline is an error value for measuring distances between lines.
            #self.intraline is an error value for other vertical measurements.
            #self.horizontal is an error value for horizontal measurements, such as between words.
            self.linespace, self.lineratio, self.lineheight, self.paraAlign, self.paraSpace, self.interline, self.horizontal = FindSpace(
                pdf, vError, hError, PARAS_REQUIRED)

            self.intraline = self.linespace * .4

            #self.pageHeaders is an array of header objects (defined in this document) representing page headers.
            self.pageHeaders = FindPageHeaders(pdf, self, hError)

            #self.pageFooters is another array of header objects (defined in this document) representing page footers.
            self.pageFooters = FindPageFooters(pdf, self, hError)

            #sort the headers/footers so that we look at the longer ones first.
            self.pageHeaders = minorfunctions.sortByLen(self.pageHeaders)
            self.pageFooters = minorfunctions.sortByLen(self.pageFooters)

            #figure out whether we're checking for paragraphs based on vertical space or horizontal alignment.
            self.useSpace = False
            if(self.paraAlign == -1):
                self.useSpace = True

        #boolean used to determine whether a line of figure text is part of an existing figure caption or a new figure caption
        self.newFig = False


        #an array of citations in the current paragraph, though this functionality isn't implemented yet.
        self.cites = []

        #an array of integer indices describing the current section/subsection. 
        # i.e. Section 2.3.5 will have coords [1, 2, 4]
        self.coords = [-1]

        #a boolean determining whether a paragraph has been cutoff by the end of a column or page.
        self.addto = False

        #a placeholder boolean used in PDFfunctions.extensiveAddPara()
        self.addtoNext = False

        #a float determining the ratio between line height and line spacing for multi-line headers.
        self.consistentRatio = 0.0

        #an integer index describing which paragraph of the current section/subsection the current paragraph is.
        self.paraNum = 0

        #an integer used to determine where we are in the list of words.
        self.bookmark = 0

        #an integer used to determine how many words have been removed from the array of words.
        self.offset = 0

        #a section object used so that we can add subsections/paragraphs to that.
        self.activesection = PDFfragments.section("")


# expect_num is whether the text right after the header is a page number.
# text is... it's the words, isn't it...
class Header():
    def __init__(self, text, expect_num=False):
        self.text = text
        self.expect_num = expect_num

    def __eq__(self, other):
        return minorfunctions.reverseArr(self.text, "text") == minorfunctions.reverseArr(other.text, "text") and self.expect_num == self.expect_num


#Finds page headers.
def FindPageHeaders(pdf, pdfSettings, hError):
    headers = []
    for i in range(len(pdf.pages)-4):

        #get the words from the pages you're looking for.
        if(i == 0):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)
        else:
            #don't keep running getWords() if you don't need to.
            words = words2
            words2 = words3
            words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)

        #figure out if there's a header there.
        headers, foundHeader = addHeader(headers, words, i, words2, words3)

        #if there isn't one, try looking backwards.
        if(not foundHeader and i >= 4):
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    #the last 4 pages will have to look backwards for headers, since we can't look ahead if we're at the end.
    if(len(pdf.pages) > 4):
        for i in range(len(pdf.pages)-4, len(pdf.pages)):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            headers, foundHeader = addHeader(headers, words, i, words2, words3)

    return headers


#headers is the array we're adding to.
#words is the array of words.
#i is the page number of the words array.
#words2 is the words on page i+2 (or i-2 if there is no page i+2)
#words3 is the words on page i+4 (or i-4 if there is no page i+4)
def addHeader(headers, words, i, words2, words3):
    visible1 = words[len(words)-240:]
    visible2 = words2[len(words2)-240:]
    visible3 = words3[len(words3)-240:]

    index = 0
    first1 = words[0]
    expect_num = False
    foundHeader = False

    #if there's a page number at the beginning, move beyond it.
    if first1["text"].isdigit():
        if(int(first1["text"]) == first1["Page"]):
            index += 1
    
    #check whether there is a header but it's just that the first word or so doesn't line up.
    anyHeader = False
    x, offset = checkForHeaderOffset(words, words2, words3, index)

    #check to see if there's a header.
    if headerCheck(words, words2, words3, index, offset):
        anyHeader = True

    #if we found a potential header, find the rest of it.
    if anyHeader:
        oldOffset = offset
        foundHeader = True
        count = index
        k = index

        #for each word in the potential header
        while k < len(words):
            k += 1
            #check to see whether this word lines up. If it does, keep going.
            if headerCheck(words, words2, words3, k, oldOffset):
                count += 1
                continue

            #if it doesn't, see whether it'll line up later. If it does, adjust offset and keep going.
            x, newOffset = checkForHeaderOffset(words, words2, words3, k)
            if(newOffset != 0 and newOffset != oldOffset):
                oldOffset = newOffset
                k -= x

            #if it doesn't but we hit a page number, mark that and end the searching.
            elif(words[len(words)-k]["text"].isdigit() and words[len(words)-k]["text"] == str(i+1)) or (words[len(words)-k]["text"][0:len(str(i+1))] == str(i+1) or words[len(words)-1]["text"][0:len(str(i+1))] == str(i+1)):
                expect_num = True
                break
            #otherwise end the searching.
            else:
                break

        #get the text we found and turn it into a header.
        text = words[index:count+1]

        #add the new header to the list unless it's there already.
        headers = minorfunctions.appendNoRepeats(
            Header(text, expect_num), headers)

    return headers, foundHeader

# really long if statement, checks that words[index] is equal on all 3 pages or that they're all numbers.
def headerCheck(words, words2, words3, index, offset=0):
    if(index < 0):
        index = 0

    #get the words.
    w1 = words[index+offset]
    w2 = words2[index]
    w3 = words3[index]

    #get text from the words
    t1, t2, t3 = w1["text"], w2["text"], w3["text"]

    #get the words' heights.
    h1, h2, h3 = w1["bottom"] - w1["top"], w2["bottom"] - w2["top"], w3["bottom"] - w3["top"]

    #if the text is the same, we're good.
    if t1 == t2 and t2 == t3 and minorfunctions.listElementsEqual([h1, h2, h3], 5, True):
        return True

    #if not, get rid of any subscript/superscript
    t1 = textprocessing.trimScript(t1)
    t2 = textprocessing.trimScript(t2)
    t3 = textprocessing.trimScript(t3)

    #then check to see if they're all numbers and they're within 4 of each other. In this case, they're page numbers.
    if t1.isdigit() and t2.isdigit() and t3.isdigit():
        if(minorfunctions.listElementsEqual([int(t1), int(t2), int(t3)], 4)):
            if(minorfunctions.listElementsEqual([h1, h2, h3], 5, True)):
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


#same as FindPageHeaders, but looking at the end of the lists of words instead of the beginning.
def FindPageFooters(pdf, pdfSettings, hError):
    footers = []
    for i in range(len(pdf.pages)-4):
        if(i == 0):
            words = PDFfunctions.getWords(pdf.pages[i], hError)
            words2 = PDFfunctions.getWords(pdf.pages[i+2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)
        else:
            #cut down on the number of times we have to call the time-consuming function.
            words = words2
            words3 = words2
            words3 = PDFfunctions.getWords(pdf.pages[i+4], hError)

        #this is for debugging purposes.
        visible1 = words[len(words)-240:]
        visible2 = words2[len(words2)-240:]
        visible3 = words3[len(words3)-240:]

        #try to find a footer.
        footers, foundFooter = addFooter(footers, words, i, words2, words3)

        #if we didn't find one, try looking backwards.
        if(not foundFooter and i >= 4):
            words2 = PDFfunctions.getWords(pdf.pages[i-2], hError)
            words3 = PDFfunctions.getWords(pdf.pages[i-4], hError)
            footers, foundFooter = addFooter(footers, words, i, words2, words3)

        #if we didn't find one and we're at the beginning of the doc, try at least seeing if pages 1 and 2 share a footer.
        if(not foundFooter and (i == 0 or i == 1)):
            words2 = PDFfunctions.getWords(pdf.pages[0], hError)
            words3 = PDFfunctions.getWords(pdf.pages[1], hError)
            footers, foundFooter = addFooter(footers, words, i, words2, words3)


    #for the last 4 pages we're gonna look backwards all the time cuz we can't look forwards.
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



#try to find if the words are just a little bit off.
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


#try to find it the words are just a little bit off.
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
