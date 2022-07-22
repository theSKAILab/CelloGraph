from typing import Reversible
import copy
import re
import textprocessing
import minorfunctions


# CLASSES



# PDFdocument is the big class where one instance of it will have access to all the text.
class PDFdocument:
    def __init__(self):
        # Array of Section objects (see class definition below)
        self.sections = []
        # Array of Figure objects (see class definition below)
        self.figures = []

        # Array of tables, each of which is a tuple. [0] is the table (2d array), [1] is the page the table appears on (Integer).
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
        notcoords.append(0)

        for subhead in head.subsections:
            notcoords[len(notcoords)-1] += 1
            retval += self.getSectionText(notcoords)

        return retval

    # returns a list of all the citations from all the sections.
    # Not currently used, as citations are currently not used.
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
        #string of "what is the section header"
        self.title = t
        #array of section objects.
        self.subsections = []
        #section object that is the parent of this section, i.e. Section 2 is the parent of Section 2.3
        self.parent = p
        # Array of Paragraph objects
        self.para = []
        # Integer describing what kind of section this is. i.e. Section 2 will have type 1, Section 5.3 will have type 2.
        self.type = type
        # array of integer indices describing where this section is. i.e. section 2 will have [1] section 3.5 will have [2, 4]
        self.coords = coords
        # a float describing how tall the section header text is.
        self.height = h

        #integer: what page is this on. NOT AN INDEX
        self.pagenum = pagenum

        #integer: what column is this in. NOT AN INDEX
        self.colnum = colnum


    #This is an == override.
    def __eq__(self, other):
        if(minorfunctions.xor(self, other)):
            return False
        
        #If they're mostly equal
        if self.title == other.title and self.type == other.type and self.coords == other.coords and self.height == other.height and self.pagenum == other.pagenum:
            #check if their parents are equal
            if(self.parent and other.parent):
                if(not self.parent.lightEq(other.parent)):
                    return False
            if(minorfunctions.xor(self.parent, other.parent)):
                return False
            
            #check if their subsections are equal
            if(len(self.subsections) == len(other.subsections)):
                for i in range(len(self.subsections)):
                    if(self.subsections[i] != other.subsections[i]):
                        return False
                return True
        return False

    # this is a version of eq that doesn't use recursion so we can check if parent sections are equal
    def lightEq(self, other):
        if(minorfunctions.xor(self, other)):
            return False
        if(not self and not other):
            return True

        if self.title == other.title and self.type == other.type and self.coords == other.coords and self.height == other.height and self.pagenum == other.pagenum and len(self.subsections) == len(other.subsections):
            return True
        return False

# returns (last subsection, last subsection's type)

    def lastsub(self):
        if(len(self.subsections) == 0):
            return (None, None)
        return (self.subsections[len(self.subsections)-1], self.type+1)

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

    def copy(self):
        titlecopy = copy.copy(self.title)
        parent = self.parent
        paracopy = []
        for i in range(len(self.para)):
            paracopy.append(copy.copy(self.para[i]))
        typecopy = copy.copy(type)
        subsections = []
        for i in range(len(self.subsections)):
            subsections.append(self.subsections[i].copy())
        retval = section(titlecopy, parent, typecopy, ratiocopy)
        retval.para = paracopy
        retval.subsections = subsections
        return retval


# sentences: an array of sentences.
# coords: an array of ints that indicate which section the paragraph is from
# paraNum: the index of this paragraph within its section
# citations: an array of citations
class paragraph:
    def __init__(self, coords, paraNum, sent=[], cites=[], align=0, start=[0, 0], end=[0, 0]):
        # Array of Sentence objects
        self.sentences = sent

        # array of integer indices describing where this section is. i.e. section 2 will have [1] section 3.5 will have [2, 4]
        self.coords = coords

        #an integer describing which paragraph of the section this is.
        self.paraNum = paraNum

        #an array of citation objects; NOT USED CURRENTLY
        self.citations = cites

        #a Decimal.decimal object describing how far indented the first line of the paragraph is.
        self.align = align

        #Integers describing which page and column the paragraph starts and ends on.
        self.startPage = start[0]
        self.startCol = start[1]
        self.endPage = end[0]
        self.endCol = end[1]

    def __eq__(self, other):
        if(self.coords == other.coords and self.paraNum == other.paraNum and len(self.sentences) == len(other.sentences)):
            for i in range(len(self.sentences)):
                if(self.sentences[i] != other.sentences[i]):
                    return False
            return True
        return False



#Not currently used
class citation:
    def __init__(self, words, coords=[1], paraNum=0):
        self.words = words
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
        #Array of word dictionaries (explained at bottom of this document)
        self.words = words
        #A string of this sentence's text.
        self.text = text
        # coords is an array of integer storing the sections where it is, i.e. Section 2.3 will have coords [2, 3]
        self.coords = coords
        #integer describing which paragrpah this sentence is is.
        self.para = para
        #integer describing which sentence of the paragraph this is.
        self.sentNum = sentNum

        #Integers describing which page and column the paragraph starts and ends on.
        self.startPage = start[0]
        self.startCol = start[1]
        self.endPage = end[0]
        self.endCol = end[1]

    # definition for ==
    def __eq__(self, other):
        if(self.coords == other.coords and self.sentNum == other.sentNum and self.para == other.para and self.text == other.text):
            return True
        return False

    # definition for +=
    def __iadd__(self, other):
        self.text += other.text
        self.words += other.words
        self.endCol = other.endCol
        self.endPage = other.endPage
        self.end = [self.endPage, self.endCol]
        return self




class figure:
    def __init__(self, words, pagenum, colnum):
        #figure caption as an array of word dictionaries (explained at the bottom of this document.)
        self.words = words
        #integer for what page this is on
        self.pagenum = pagenum
        #string for the figure caption
        self.text = ""
        #the figure caption but as sentence objects.
        self.sentences = []
        #integer for what column this is in.
        self.col = colnum


        self.configure()


    # turns self.words into a string, makes it self.text
    # also turns self.words into sentences, makes it self.sentences.
    # part makes it work on only the last (part) words.

    def configure(self, part=0):
        #if we're doing the whole thing, do the whole thing.
        if(part == 0 or part > len(self.words)):
            #reset self.text, then add all the words to text.
            self.text = ""
            for word in self.words:
                self.text += word["text"]
                if(self.text[len(self.text)-1] != ' '):
                    self.text += ' '
        else:
            #add the new words to text without resetting text.
            for i in range(len(self.words)-part, len(self.words)):
                word = self.words[i]
                self.text += word["text"]
                if(self.text[len(self.text)-1] != ' '):
                    self.text += ' '

        #make the words into sentences.
        nonzero = textprocessing.MakeSentences(
            self.words[len(self.words)-1-part:], [], -1, self.pagenum, self.col)

        #add the sentences to the list
        if(nonzero):
            self.sentences += nonzero

        #clean them up a bit.
        self.sentences = textprocessing.stitchSentences(self.sentences)

    # adds words to the figure, tells it to configure only the new words.
    def addWords(self, words):
        prevsize = len(self.words)
        self.words += words
        self.configure(len(self.words)-prevsize)



#WORD DICTIONARY
#see PDFfunctions.makeWord() and PDFfunctions.getWords() for more details.
# "page" = Integer. What page is this word on.
# "text" = String. The word but in string form.
# "chars" = Array of pdfPlumber char dictionaries. What characters are in this word.

#COORDINATE SYSTEM
# Moving right is moving in the positive direction, i.e. things to the right will have higher numbers.
# Moving down is moving in the positive direction, i.e. things further down will have higher numbers.

# "x0" = leftmost coordinate of the leftmost character.
# "x1" = rightmost coordinate of the rightmost character.
# "top"
# "bottom"

# "Subscript" and "Superscript" are booleans used to attach subscript/superscript to other words.

# "Pieces" is an array of strings detailing which pieces of the word are subscript/superscript. 
# i.e. 10^12 will have pieces ["10", "12"]


#LINE DICTIONARY
#Because I get words and then organize them into lines, each line dictionary is pretty specific to that words array.
#see PDFfunctions.getLines() and PDFfunctions.addLine() for more details.


# "LineStartDex" = Integer index. index of the first word of this line in the words array.
# "LineEndDex" = Integer index. index of the last word of this line in the words array.

# "AftSpace" = Decimal.decimal object. Amount of space after this line.
# "BefSpace" = Decimal.decimal object. Amount of space before this line.

# "Height" = Decimal.decimal object. How tall this line is.
# "AftRatio" = float Height / AftSpace
# "BefRatio" = float Height / BefSpace

# "Align" = Decimal.decimal object. The x0 coordinate of the first word on this line
# "Words" = Array of word dictionaries. Each word in this line.
# "Cutoff" = Boolean. Describes whether the last word on this line has been cutoff.

