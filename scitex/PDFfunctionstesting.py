import PDFfunctions
import PDFfragments
import pdfplumber
from pdfplumber.utils import extract_text

# addLine(lines, words, prevLineBegin, currentLineBegin, nextLineBegin, w):


class addLineTester():
    def reset(self):
        self.lines = []
        self.words = []
        self.prev = 0
        self.current = 0
        self.next = 0
        self.w = 0

    def allTest(self):
        self.emptyWordsTest()
        self.beginTest()
        self.endTest()
        self.midTest()

    def emptyWordsTest(self):
        self.reset()
        assert len(PDFfunctions.addLine(self.lines, self.words,
                   self.prev, self.current, self.next, self.w)[0]) == 0

    def beginTest(self):
        self.reset()
        pdf = pdfplumber.open("scitex/test/loremIpsum.pdf")
        words = PDFfunctions.getWords(pdf.pages[0], 10)
        next = 12
        w = 26
        self.lines = PDFfunctions.addLine(self.lines, words, 0, 0, next, w)[0]

        assert len(self.lines) == 1 and len(self.lines[0]["Text"]) == 12

        current = 12
        next = 26
        w = 39
        self.lines = PDFfunctions.addLine(
            self.lines, words, 0, current, next, w)[0]

        assert len(self.lines) == 2 and len(self.lines[1]["Text"]) == 14

    def endTest(self):
        self.reset()
        pdf = pdfplumber.open("scitex/test/loremIpsum.pdf")
        words = PDFfunctions.getWords(pdf.pages[0], 10)
        prev = 39
        current = 52
        next = 65
        w = len(words)
        self.lines = PDFfunctions.addLine(
            self.lines, words, prev, current, next, w)[0]

        assert len(self.lines) == 1 and len(self.lines[0]["Text"]) == 13

        prev = 52
        current = 65
        next = len(words)
        self.lines = PDFfunctions.addLine(
            self.lines, words, prev, current, next, w)[0]

        assert len(self.lines) == 2 and len(self.lines[1]["Text"]) == 4

    def midTest(self):
        self.reset()
        pdf = pdfplumber.open("scitex/test/loremIpsum.pdf")
        words = PDFfunctions.getWords(pdf.pages[0], 10)
        prev = 12
        current = 26
        next = 39
        w = 52
        self.lines = PDFfunctions.addLine(
            self.lines, words, prev, current, next, w)[0]

        assert len(self.lines) == 1 and len(self.lines[0]["Text"]) == 13


alt = addLineTester()
alt.allTest()

# makeWord(chars)


class makeWordTester():
    def __init__(self):
        pdf = pdfplumber.open("scitex/test/wordTest.pdf")
        self.chars = pdf.chars

    def allTest(self):
        self.emptyTest()
        self.nonEmptyTest()
        self.multiwordTest()

    def emptyTest(self):
        chars = []
        assert PDFfunctions.makeWord(chars) == None

    def multiwordTest(self):
        assert PDFfunctions.makeWord(self.chars)["text"] == "Hello"

    def nonEmptyTest(self):
        assert PDFfunctions.makeWord(self.chars[:5])["text"] == "Hello"


mwT = makeWordTester()
mwT.allTest()


class Page():
    def __init__(self):
        self.chars = []
        self.page_number = 0


class getWordsTester():
    def allTest(self):
        self.emptyTest()
        self.loremTest()
        self.scriptTest1()

    def scriptTest1(self):
        pdf = pdfplumber.open("scitex/test/scriptTest1.pdf")
        words = PDFfunctions.getWords(pdf.pages[0], 10)
        assert len(words) == 12

    def loremTest(self):
        pdf = pdfplumber.open("scitex/test/loremIpsum.pdf")
        assert len(PDFfunctions.getWords(pdf.pages[0], 10)) == 69

    def emptyTest(self):
        page = Page()
        assert len(PDFfunctions.getWords(page, 10)) == 0


gwt = getWordsTester()
# gwt.allTest()


class cleanSectionTester():
    def allTest(self):
        self.emptyTest()
        self.noneToRemoveTest()
        self.removeFromSubTest()
        self.removeFromSecTest()
        self.removeFromBothTest()

    def emptyTest(self):
        sec = PDFfragments.section("Section")
        clean = PDFfunctions.cleanSection(sec)
        assert sec == clean

    def noneToRemoveTest(self):
        sec = PDFfragments.section("Section")
        s1 = PDFfragments.sentence("Hello there, I'm a sentence.", [0], 0, 0)
        p1 = PDFfragments.paragraph([0], 0, [s1])
        sec.para.append(p1)
        clean = PDFfunctions.cleanSection(sec)
        assert len(clean.para) == 1

    def removeFromSubTest(self):
        sec = PDFfragments.section("Section")
        sub = PDFfragments.section("Subsection", sec)
        s1 = PDFfragments.sentence("Hello there, I'm a sentence.", [0], 0, 0)
        p1 = PDFfragments.paragraph([0], 0, [s1])
        p2 = PDFfragments.paragraph([0, 0], 0)
        sec.para.append(p1)
        sub.para.append(p2)
        sec.subsections.append(sub)
        clean = PDFfunctions.cleanSection(sec)
        assert len(clean.subsections[0].para) == 0

    def removeFromSecTest(self):
        sec = PDFfragments.section("Section")
        p1 = PDFfragments.paragraph([0], 0)
        sec.para.append(p1)
        clean = PDFfunctions.cleanSection(sec)
        assert len(clean.para) == 0

    def removeFromBothTest(self):
        sec = PDFfragments.section("Section")
        sub = PDFfragments.section("Subsection", sec)
        sec.subsections.append(sub)
        p1 = PDFfragments.paragraph([0], 0)
        p2 = PDFfragments.paragraph([0, 0], 0)
        sec.para.append(p1)
        sub.para.append(p2)
        clean = PDFfunctions.cleanSection(sec)
        assert len(clean.para) == 0
        assert len(clean.subsections[0].para) == 0


cst = cleanSectionTester()
cst.allTest()


class recRemoveFigHeadTester():
    def allTest(self):
        self.emptyTest()
        self.noneToRemoveTest()
        # self.removeFromSecTest()
        # self.removeFromSubTest()
        # self.removeFromBothTest()

    def emptyTest(self):
        PDF = PDFfragments.PDFdocument()
        sec = PDFfragments.section("Section")
        assert PDFfunctions.recursiveRemoveFigureHeaders(
            PDF, sec) == (PDF, sec)

    def noneToRemoveTest(self):
        PDF = PDFfragments.PDFdocument()
        sec = PDFfragments.section("Section")

    # def removeFromSecTest(self):

    # def removeFromSubTest(self):

    # def removeFromBothTest(self):


rrfht = recRemoveFigHeadTester()
rrfht.allTest()

#
#    # DealWithMultiLineFigureHeader(section):
#
#
# class DealWithMultiLineFigureHeaderTester():
#
#    # removeFigureHeaders(PDF):
#
#


class removeFigHeadTester():
    def allTest(self):
        self.emptyTest()
        self.singleFigureTest()
        self.multiFigureTest()
        self.removefromSubTest()

    def emptyTest(self):
        PDF = PDFfragments.PDFdocument()
        assert PDFfunctions.removeFigureHeaders(
            PDF) == PDFfragments.PDFdocument()

    def singleFigureTest(self):
        PDF = PDFfragments.PDFdocument()
        sec1 = PDFfragments.section("1. Intro")
        sec2 = PDFfragments.section("Figure 1. ABBA")
        sec3 = PDFfragments.section("Fig. 2 ABBA stands for Abacus")
        sec4 = PDFfragments.section("2. Conclusion")
        PDF.sections.append(sec1)
        PDF.sections.append(sec2)
        PDF.sections.append(sec3)
        PDF.sections.append(sec4)
        PDF2 = PDFfragments.PDFdocument()
        PDF2.sections.append(sec1)
        PDF2.sections.append(sec4)
        PDF = PDFfunctions.removeFigureHeaders(PDF)
        assert PDF == PDF2

    def multiFigureTest(self):
        PDF = PDFfragments.PDFdocument()
        sec1 = PDFfragments.section("1. Intro")
        sec2 = PDFfragments.section("Figure 1. ABBA")
        sec3 = PDFfragments.section("2. Conclusion")

        sent1 = PDFfragments.sentence(
            "plays onstage for the first time in 32 years.", [0], 0, 0)
        para1 = PDFfragments.paragraph([0], 0, [sent1])

        sec2.para.append(para1)
        PDF.sections.append(sec1)
        PDF.sections.append(sec2)
        PDF.sections.append(sec3)
        PDF = PDFfunctions.removeFigureHeaders(PDF)
        assert len(PDF.sections) == 2
        for i in range(len(PDF.sections)):
            assert len(PDF.sections[i].para) == 0

    def removefromSubTest(self):
        PDF = PDFfragments.PDFdocument()
        sec1 = PDFfragments.section("1. Intro")
        sec2 = PDFfragments.section("Figure 1. ABBA")
        sec3 = PDFfragments.section("2. Conclusion")

        sent1 = PDFfragments.sentence(
            "plays onstage for the first time in 32 years.", [0], 0, 0)
        para1 = PDFfragments.paragraph([0], 0, [sent1])

        sec2.para.append(para1)
        PDF.sections.append(sec1)
        PDF.sections[0].subsections.append(sec2)
        PDF.sections.append(sec3)
        PDF = PDFfunctions.removeFigureHeaders(PDF)
        for i in range(len(PDF.sections)):
            assert len(PDF.sections[i].para) == 0


rfht = removeFigHeadTester()
rfht.allTest()

#
#    # recursiveRemovePara(section, coords, paraNum):
#
#
# class recursiveRemoveParaTester():
#
#    # recursiveRemoveSentence(section, coords, paraNum, sentNum):
#
#
# class recursiveRemoveSentenceTester():
#    # removePageHeaderSentences(PDF):
#
#
# class removePageHeaderSentencesTester():
#    # removeDuplicateHeaders(PDF):
#
#
# class removeDuplicateHeadersTester():
#
#    # addSection(header, title, type, PDF, pdfSettings, h=3, pagenum=1, recursionlevel=0):
#
#
# class addSectionTester():
#
#    # moveSection(tomove, destination):
#
#
# class moveSectionTester():
#
#
#


class newlineTester():
    def __init__(self):
        pdf = pdfplumber.open("scitex/test/loremIpsum.pdf")
        self.words = PDFfunctions.getWords(pdf.pages[0], 10)
        self.error = 2

    def allTest(self):
        self.emptyTest()
        self.firstWordTest()
        self.lastWordTest()
        self.properTest()
        self.scriptTest1()

    def emptyTest(self):
        words = []
        assert PDFfunctions.newline(words, 10, self.error) == False

    def firstWordTest(self):
        assert PDFfunctions.newline(self.words, 0, self.error) == False

    def lastWordTest(self):
        assert PDFfunctions.newline(self.words, len(
            self.words)-1, self.error) == False

    def properTest(self):
        assert PDFfunctions.newline(self.words, 12, self.error) == True

    def scriptTest1(self):
        pdf = pdfplumber.open("scitex/test/scriptTest1.pdf")
        self.words = PDFfunctions.getWords(pdf.pages[0], 10)
        for w in range(len(self.words)):
            assert PDFfunctions.newline(self.words, w, self.error) == False


nlt = newlineTester()
nlt.allTest()

#    # removeTables(PDF, page, words, error):
#
#
# class removeTablesTester():
#
#    # CutWords(large, small):
#
#


class CutWordsTester():
    def allTest(self):
        self.emptyTest()
        self.reverseTest()
        self.normalTest()
        self.unequalTest()

    def emptyTest(self):
        assert PDFfunctions.CutWords([], []) == []

    def reverseTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "Hello"}, {"text": "there"}]
        cut = PDFfunctions.CutWords(short, long)
        assert cut == [{"text": "today's"}, {"text": "Monday."}]

    def normalTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "Hello"}, {"text": "there"}]
        cut = PDFfunctions.CutWords(long, short)
        assert cut == [{"text": "today's"}, {"text": "Monday."}]

    def unequalTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "UmActually"}]
        cut = PDFfunctions.CutWords(long, short)
        assert cut == [{"text": "Hello"}, {"text": "there"},
                       {"text": "today's"}, {"text": "Monday."}]


cwt = CutWordsTester()
cwt.allTest()


class CutWordsEndTester():
    def allTest(self):
        self.emptyTest()
        self.reverseTest()
        self.normalTest()
        self.unequalTest()

    def emptyTest(self):
        assert PDFfunctions.CutWordsEnd([], []) == []

    def reverseTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "today's"}, {"text": "Monday."}]
        cut = PDFfunctions.CutWordsEnd(short, long)
        assert cut == [{"text": "Hello"}, {"text": "there"}]

    def normalTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "today's"}, {"text": "Monday."}]
        cut = PDFfunctions.CutWordsEnd(long, short)
        assert cut == [{"text": "Hello"}, {"text": "there"}]

    def unequalTest(self):
        long = [{"text": "Hello"}, {"text": "there"},
                {"text": "today's"}, {"text": "Monday."}]
        short = [{"text": "UmActually"}]
        cut = PDFfunctions.CutWordsEnd(long, short)
        assert cut == [{"text": "Hello"}, {"text": "there"},
                       {"text": "today's"}, {"text": "Monday."}]


cwet = CutWordsEndTester()
cwet.allTest()

#
#    # removePageHeadersEarly(words, num, pdfSettings):
#
#
# class removePageHeadersEarlyTester():
#
