from typing import Reversible
import copy
import re
import textprocessing
import minorfunctions


# CLASSES



# PDFdocument is the big class where one instance of it will have access to all the text.
class PDFdocument:
    def __init__(self):
        self.sections = []
        self.figures = []
        self.tables = []

    # just returns the last section, unless there aren't any.
    def lastSect(self):
        if(len(self.sections) != 0):
            return self.sections[len(self.sections)-1]
        else:
            return section("")

    # same as lastSect but for figures.
    def lastFig(self):
        if(len(self.figures) != 0):
            return self.figures[len(self.figures)-1]
        else:
            return figure("", -1, 0)

    # had to make my own equality function smh
    def __eq__(self, other):
        if(len(self.sections) != len(other.sections)):
            return False
        if(len(self.figures) != len(other.figures)):
            return False
        if(len(self.figures) != len(other.figures)):
            return False
        for i in range(len(self.sections)):
            if(self.sections[i] != other.sections[i]):
                return False

        return True

    # takes an array of coordinates that lead to the appropriate section, then assembles the text of that section into one string
    # coords: an array of up to three numbers indicating a specific section or subsection
    # para: the index of the specific paragraph requested
    # sent: the index of the specific sentence requested
    def getSectionText(self, coords, para=-1, sent=-1):
        # set some variables for convinience
        if(len(coords) == 1):
            head = self.sections[coords[0]]
        elif(len(coords) == 2):
            head = self.sections[coords[0]].subsections[coords[1]]
        elif(len(coords) == 3):
            head = self.sections[coords[0]
                                 ].subsections[coords[1]].subsections[coords[2]]
        else:
            return "ERROR: Array too long"

        retval = head.title + "\n\n"

        # if they've requested a specific paragraph, then give it to them
        if(para != -1 and sent == -1):
            return textprocessing.makeString(head.para[para].sentences, "class")
        # if they've requested a specific paragraph and sentence, then give it to them
        if(para != -1 and sent != -1):
            return head.para[para].sentences[sent].text
        # if they requested a sentence, but not a paragraph, then give them that sentence from the first paragraph
        if(para == -1 and sent != -1):
            return head.para[0].sentences[sent].text

        # get all the text between the section and the first subsection
        for p in range(len(head.para)):
            retval += textprocessing.makeString(
                head.para[p].sentences, "class")
            retval += "\n\n"

        # get all the text from subsections
        notcoords = copy.copy(coords)
        notcoords.append(-1)

        for subhead in head.subsections:
            notcoords[len(notcoords)-1] += 1
            retval += self.getSectionText(notcoords)

        return retval

    # takes coordinates and provides an array of sentences. If one specific sentence is requested then it just returns that.
    # coords: an array of up to three numbers that indicates a specific section
    # para: the index of a specific paragraph within a section
    # sent: the index of a specific sentence within a paragraph

    def getSentences(self, coords, para=0, sent=-1):
        # set some variables for convinience
        head = self.sections[coords[0]]
        for i in range(1, len(coords)):
            head = head.subsections[coords[i]]

        retval = []
        # if they haven't specified a sentence, give them all sentences from that paragraph
        if(sent == -1):
            for s in head.para[para]:
                retval.append(s)
            return retval
        # if they have specified a sentence, then give it to them
        if(sent != -1):
            return head.para[para].sentences[sent]

        retval = [head.title]
        # get all the text between the section and the first subsection
        for p in head.para:
            for s in p.sentences:
                retval += head.para.sentences

        # get all the text from subsections
        coords.append(0)
        for subhead in head.subsections:
            retval += self.getSentences(coords)
            coords[len(coords)] += 1

        return retval

    # returns a list of all the citations from all the sections.
    def getCite(self):
        retval = []
        for h in self.sections:
            arr = h.getCite()
            for cite in arr:
                retval.append(cite)
        return retval


# section

# fields
# title: A string to hold the section text
# subsections: an array of subsections that fall under the section (each 'subsection' is of type section)
# parent: if instance is a subsection, then parent points to the main section
# para: an array of paragraphs between this section and the next

class section:
    def __init__(self, t, p=None, coords=[], type=0, h=3, pagenum=1, colnum=0):
        self.title = t
        self.subsections = []
        self.parent = p
        self.para = []
        self.type = type
        self.coords = coords
        self.height = h
        self.pagenum = pagenum
        self.colnum = colnum

    def __eq__(self, other):
        #If only one of them is None, return false.
        if(minorfunctions.xor(self, other)):
            return False

        #if they're mostly the same, then do some more checking.
        if self.title == other.title and self.type == other.type and self.coords == other.coords and self.height == other.height and self.pagenum == other.pagenum:
            
            #this is two if statements because I can't call lightEq unless self.parent and other.parent are true.
            if(self.parent and other.parent):
                #if the parent sections are different, return False.
                if(not self.parent.lightEq(other.parent)):
                    return False

            #If only one of them has a parent, return false.
            if(minorfunctions.xor(self.parent, other.parent)):
                return False    

            #If the subsections are the same, return True. Else, return false.
            if(len(self.subsections) == len(other.subsections)):
                for i in range(len(self.subsections)):
                    if(self.subsections[i] != other.subsections[i]):
                        return False
                return True
        return False

    # this is a version of eq that doesn't use recursion
    # used to check whether parent sections are equal without going infinite.
    def lightEq(self, other):
        if(not self and not other):
            return True
        elif(not self or not other):
            return False
        if self.title == other.title:
            if(self.type == other.type):
                if(self.coords == other.coords):
                    if(self.height == other.height):
                        if(self.pagenum == other.pagenum):
                            if(len(self.subsections) == len(other.subsections)):
                                return True
        return False



# returns (last subsection, last subsection's type)

    def lastsub(self):
        if(len(self.subsections) == 0):
            return (None, None)
        return (self.subsections[len(self.subsections)-1], self.type+1)

# getCite() returns an array of all citations in this section and in all subsections.
# currently unused cuz I don't have citations working properly yet.
    def getCite(self):
        retval = []
        for para in self.para:
            add = para.getCite()
            for cite in add:
                retval.append(cite)
        for sub in self.subsections:
            add = sub.getCite()
            for cite in add:
                retval.append(cite)
        return retval

    #returns a copy of the section.
    #I don't believe I actually use this for anything, given that it's had an error for a long time.
    #def copy(self):
    #    titlecopy = copy.copy(self.title)
    #    parent = self.parent
    #    paracopy = []
    #    for i in range(len(self.para)):
    #        paracopy.append(copy.copy(self.para[i]))
    #    typecopy = copy.copy(type)
    #    subsections = []
    #    for i in range(len(self.subsections)):
    #        subsections.append(self.subsections[i].copy())
    #    retval = section(titlecopy, parent, typecopy, ratiocopy)
    #    retval.para = paracopy
    #    retval.subsections = subsections
    #    return retval


# sentences: an array of sentences.
# coords: an array of ints that indicate which section the paragraph is from
# paraNum: the index of this paragraph within its section
# citations: an array of citations
class paragraph:
    def __init__(self, coords, paraNum, sent=[], cites=[], align=0, start=[0, 0], end=[0, 0]):
        #an array of sentence objects
        self.sentences = sent

        #an array of integer indices describing which section/subsection this paragraph is in.
        #i.e. Section 3.4.1 will have coords [2, 3, 0]
        self.coords = coords

        #an integer index describing which paragraph in the section this is.
        self.paraNum = paraNum

        #An array of citation objects that occur within this paragraph. Currently unused.
        self.citations = cites

        #A Decimal.decimal object. The x coordinate of the first line of the paragraph, used to measure indent.
        self.align = align

        #Integers describing which page and column the paragraph starts and ends on. NOT INDICES
        self.startPage = start[0]
        self.startCol = start[1]
        self.endPage = end[0]
        self.endCol = end[1]

    def __eq__(self, other):
        if(self.coords == other.coords):
            if(self.paraNum == other.paraNum):
                if(len(self.sentences) == len(other.sentences)):
                    for i in range(len(self.sentences)):
                        if(self.sentences[i] != other.sentences[i]):
                            return False
                    return True
        return False

    def getText(self):
        retval = ""
        for s in self.sentences:
            retval += s.text + " "
        return retval

    def getPlace(self):
        retval = "Section: "
        for i in self.coords:
            retval += str(i+1) + "."
        retval = " Paragraph: " + str(self.paraNum + 1)

    # putting in nothing for num will return all sentences
    # putting in a number will return that sentence, i.e. 1 will return the first
    def getSentence(self, num=-1):
        if(num == -1):
            return self.sentences
        return self.sentences[num-1]

    # putting in a citation for text will return that citation, if it exists
    # putting in nothing for text will return all citations.
    def getCite(self, text="-1"):
        if(text == "-1"):
            return self.citations
        else:
            pattern = "[" + text + "]"
            for cite in self.citations:
                if cite.text == pattern:
                    return cite
        return "Error: Citation not found"


class citation:
    def __init__(self, text, coords=[0], paraNum=0):
        self.text = text
        self.coords = coords
        self.paraNum = paraNum

    def getPlace(self):
        retval = "Section: "
        for i in self.coords:
            retval += str(i+1) + "."
        retval = " Paragraph: " + str(self.paraNum + 1)


# text: A string containing the sentence
# coords: an array of up to three numbers indicating which section this sentence is from
# para: the index of the paragraph this sentence is from within its section
# sentNum: the index of this sentence within the paragraph its from

class sentence:
    def __init__(self, words, text, coords, para, sentNum, start=[0, 0], end=[0, 0]):
        #an array of dictionaries, defined in PDFfunctions.makeWord
        self.words = words

        #a string of the sentence's text.
        self.text = text

        # an array of integers describing which section/subsection the sentence is located in.
        #i.e. Section 2.3 would have coords [1, 2] cuz I'm using indices (might change this tho)
        self.coords = coords

        # an integer index describing which paragraph of the section this sentence is in.
        self.para = para

        # an integer index describing which sentence this is within its paragraph.
        self.sentNum = sentNum

        # integers describing which page/column the sentence starts and ends on.
        # NOTE: these are not indices. I will be changing all of these numbers to be not indices.
        self.startPage = start[0]
        self.startCol = start[1]
        self.endPage = end[0]
        self.endCol = end[1]

    # override so u can use sent1 == sent2
    def __eq__(self, other):
        if(self.coords == other.coords):
            if(self.sentNum == other.sentNum):
                if(self.para == other.para):
                    if(self.text == other.text):
                        return True
        return False

    # override so u can use sent1 += sent2
    def __iadd__(self, other):
        self.text += other.text
        self.words += other.words
        self.endCol = other.endCol
        self.endPage = other.endPage
        self.end = [self.endPage, self.endCol]
        return self

    # getPlace: returns a string describing the location of this sentence.

    def getPlace(self):
        retval = "Section: "
        for i in self.coords:
            retval += str(i+1) + "."
        retval += " Paragraph: " + str(self.para + 1)
        retval += " Sentence: " + str(self.sentNum + 1)
        return retval


#FIGURE
class figure:
    def __init__(self, words, num, colnum):
        #an array of word dictionaries. See PDFfunctions.makeWord
        self.words = words
        self.pagenum = num
        self.text = ""
        self.sentences = []
        self.col = colnum
        self.configure()


# turns self.words into a string, makes it self.text
# also turns self.words into sentences, makes it self.sentences.
# part makes it work on only the last (part) words.

    def configure(self, part=0):
        if(part == 0 or part > len(self.words)):
            self.text = ""
            for word in self.words:
                self.text += word["text"]
                if(self.text[len(self.text)-1] != ' '):
                    self.text += ' '
        else:
            for i in range(len(self.words)-part, len(self.words)):
                word = self.words[i]
                self.text += word["text"]
                if(self.text[len(self.text)-1] != ' '):
                    self.text += ' '

        nonzero = textprocessing.MakeSentences(
            self.words[len(self.words)-1-part:], [], -1, self.pagenum, self.col)

        if(nonzero):
            self.sentences += nonzero

        self.sentences = textprocessing.stitchSentences(self.sentences)

    def addWords(self, words):
        prevsize = len(self.words)
        self.words += words
        self.configure(len(self.words)-prevsize)



# DEFINITION OF WORDS

# Words are made in PDFfunctions.makeWord()
# PDFfunctions.getWords() might provide additional insight.
# Scitex Words are dictioniaries with the following attributes:

# "Page" = an integer describing what page this word is on. NOT AN INDEX
# "text" = a string containing the text of the word.
# "chars" = an array of PDFplumber character dictionary objects that make up the word.
# "x0" = the left-x-coordinate of the leftmost character.
# "x1" = the right-x-coordinate of the rightmost character.
# "top" = the top-y-coordinate of the topmost character.
# "bottom" = the bottom-y-coordinate of the bottommost character.
# "upright" = Boolean carried over from pdfPlumber words. Not sure what it does.
# "direction" = Integer carried over from pdfPlumber words. Not sure what it does.
# "Subscript" = A boolean that describes whether this "word" is subscript.
# "Superscript" = A boolean that describes whether this "word" is superscript.
# "Pieces" = An array of strings detailing the pieces of this word, broken up depending on whether some of it is subscript/superscript/etc.
    # A word with no superscript or subscript will have one piece.


#DEFINITION OF LINES

# lines are made in PDFfunctions.addLine()
# PDFfunctions.getLines() might provide additional insight.

# Lines are dictionaries with the following attributes:

# "LineStartDex": an Integer. the index of the first word on this line.
# "LineEndDex": an Integer. the index of the last word on this line.
# "AftSpace": a Decimal.decimal object(might be a float). How much space is between this line and the next line.
# "BefSpace": A Decimal.decimal object. How much space is between this line and the previous line.
# "Height": a float. How tall is this line.
# "AftRatio": A float. Height/AftSpace
# "BefRatio": A float. Height/AftSpace
# "Align": A Decimal.decimal object. What's the x0 attribute of the first word in this line.
# "Words": An array of word objects that are on this line.
# "Cutoff": A boolean. Used to determine whether the last word on this line has been cutoff.
