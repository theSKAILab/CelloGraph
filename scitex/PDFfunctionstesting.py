import PDFfunctions
import PDFfragments

# addLine(lines, words, prevLineBegin, currentLineBegin, nextLineBegin, w):


class addLineTester():
    def reset(self):
        self.lines = []
        self.words = []
        self.prev = 0
        self.current = 0
        self.next = 0
        self.w = 0

# makeWord(chars)


class makeWordTester():

    # getWords(page, hError, spaceChar=False):


class getWordsTester():

    # words(str):


class wordsTester():

    # cleanSection(section):


class cleanSectionTester():

    # recursiveRemoveFigureHeaders(PDF, section):


class recRemoveFigHeadTester():

    # DealWithMultiLineFigureHeader(section):


class DealWithMultiLineFigureHeaderTester():

    # removeFigureHeaders(PDF):


class removeFigHeadTester():

    # recursiveRemovePara(section, coords, paraNum):


class recursiveRemoveParaTester():

    # recursiveRemoveSentence(section, coords, paraNum, sentNum):


class recursiveRemoveSentenceTester():
    # removePageHeaderSentences(PDF):


class removePageHeaderSentencesTester():
    # removeDuplicateHeaders(PDF):


class removeDuplicateHeadersTester():

    # addSection(header, title, type, PDF, pdfSettings, h=3, pagenum=1, recursionlevel=0):


class addSectionTester():

    # moveSection(tomove, destination):


class moveSectionTester():

    # newline(words, w, error):

    # returns True if words[w] is on a newline
    # def newline(words, w, error):
    #    if w == 0 or w >= len(words)-1:
    #        return False
    #    prevTop = float(words[w-1]["top"])
    #    top = float(words[w]["top"])
    #    if(minorfunctions.areEqual(top, prevTop, error)):
    #        return False
    #    bot = float(words[w]["bottom"])
    #    prevBot = float(words[w-1]["bottom"])
    #    if(minorfunctions.listElementsEqual([bot, prevBot], error)):
    #        return False
    #    return True


class newlineTester():
    def __init__(self):
        self.words = []
        self.w = 0
        self.error = 2

    def allTest(self):
        self.emptyTest()
        self.firstWordTest()
        self.LastWordTest()

    def emptyTest(self):
        words = []
        w = 0

    # removeTables(PDF, page, words, error):


class removeTablesTester():

    # CutWords(large, small):


class CutWordsTester():

    # removePageHeadersEarly(words, num, pdfSettings):


class removePageHeadersEarlyTester():
