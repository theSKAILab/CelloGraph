from typing import Reversible
import copy
import re
import PDFparser


# CLASSES


# section

# fields
# title: A string to hold the section text
# subsections: an array of subsections that fall under the section (each 'subsection' is of type section)
# parent: if instance is a subsection, then parent points to the main section
# para: an array of paragraphs between this section and the next

class section:
    def __init__(self, t, p=None, type=0, ratio=0):
        self.title = t
        self.subsections = []
        self.parent = p
        self.para = []
        self.type = type
        self.ratio = ratio

# getCite() returns an array of all citations in this section and in all subsections.
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


# sentences: an array of sentences.
# coords: an array of ints that indicate which section the paragraph is from
# paraNum: the index of this paragraph within its section
# citations: an array of citations
class paragraph:
    def __init__(self, coords, paraNum, sent=[], cites=[], align=0):
        self.sentences = sent
        self.coords = coords
        self.paraNum = paraNum
        self.citations = cites
        self.align = align

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
    def __init__(self, text, coords, para, sentNum):
        self.text = text
        self.coords = coords
        self.para = para
        self.sentNum = sentNum

    # getPlace: returns a string describing the location of this sentence
    def getPlace(self):
        retval = "Section: "
        for i in self.coords:
            retval += str(i+1) + "."
        retval += " Paragraph: " + str(self.para + 1)
        retval += " Sentence: " + str(self.sentNum + 1)
        return retval


# sections: an array of the sections within this document
class PDFdocument:
    def __init__(self):
        self.sections = []

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
            return RDFWriter.makeString(head.para[para].sentences, "class")
        # if they've requested a specific paragraph and sentence, then give it to them
        if(para != -1 and sent != -1):
            return head.para[para].sentences[sent].text
        # if they requested a sentence, but not a paragraph, then give them that sentence from the first paragraph
        if(para == -1 and sent != -1):
            return head.para[0].sentences[sent].text

        # get all the text between the section and the first subsection
        for p in range(len(head.para)):
            retval += RDFWriter.makeString(head.para[p].sentences, "class")
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


# class word

class word():
    def __init__(self, text="", coords=[]):
        self.text = text
        self.coords = coords

    def getCoords(self):
        return self.coords

    def getText(self):
        return self.text
