import minorfunctions
import PDFfragments


class EqualTester():
    def allTest(self):
        self.equalTest()
        self.greaterEqualTest()
        self.lesserEqualTest()
        self.errorEqualTest()

    def equalTest(self):
        assert minorfunctions.areEqual(8, 8) == True

    def greaterEqualTest(self):
        assert minorfunctions.areEqual(100, 102) == False
        assert minorfunctions.areEqual(100, 102, 1) == False

    def lesserEqualTest(self):
        assert minorfunctions.areEqual(100, 98) == False
        assert minorfunctions.areEqual(100, 98, 1) == False

    def errorEqualTest(self):
        assert minorfunctions.areEqual(100, 90) == False
        assert minorfunctions.areEqual(100, 90, 10) == True
        assert minorfunctions.areEqual(100, 95, 4) == False


eq = EqualTester()
eq.allTest()


class LesserTester():
    def allTest(self):
        self.equalTest()
        self.greaterTest()
        self.lesserTest()
        self.errorTest()

    def equalTest(self):
        assert minorfunctions.isLesser(8, 8) == False

    def greaterTest(self):
        assert minorfunctions.isLesser(100, 102) == True
        assert minorfunctions.isLesser(100, 102, 1) == True

    def lesserTest(self):
        assert minorfunctions.isLesser(100, 98) == False
        assert minorfunctions.isLesser(100, 98, 1) == False

    def errorTest(self):
        assert minorfunctions.isLesser(90, 100) == True
        assert minorfunctions.isLesser(90, 100, 9) == True
        assert minorfunctions.isLesser(90, 100, 11) == False


lt = LesserTester()
lt.allTest()


class GreaterTester():
    def allTest(self):
        self.equalTest()
        self.greaterTest()
        self.lesserTest()
        self.errorTest()

    def equalTest(self):
        assert minorfunctions.isGreater(8, 8) == False

    def greaterTest(self):
        assert minorfunctions.isGreater(100, 102) == False
        assert minorfunctions.isGreater(100, 102, 1) == False

    def lesserTest(self):
        assert minorfunctions.isGreater(100, 98) == True
        assert minorfunctions.isGreater(100, 98, 1) == True

    def errorTest(self):
        assert minorfunctions.isGreater(90, 100) == False
        assert minorfunctions.isGreater(100, 90, 9) == True
        assert minorfunctions.isGreater(100, 90, 11) == False


gt = GreaterTester()
gt.allTest()


class EndOfColTester():
    def allTest(self):
        self.trueTest()
        self.endTest()
        self.beyondTest()

    def trueTest(self):
        assert minorfunctions.isEndofCol(3, [1, 2, 3, 4, 5]) == False

    def endTest(self):
        assert minorfunctions.isEndofCol(1, [0, 1]) == True

    def beyondTest(self):
        assert minorfunctions.isEndofCol(30, [1, 2, 3, 4]) == True


eoct = EndOfColTester()
eoct.allTest()


class MostCommonTester():
    def allTest(self):
        self.normalTest()
        self.noMostCommonTest()
        self.emptyTest()
        self.bimodalMidTest()
        self.bimodalEndTest()

    def normalTest(self):
        list = [1, 2, 3, 3, 4, 5]
        assert minorfunctions.mostCommon(list) == 3

    def noMostCommonTest(self):
        list = [1, 2, 3, 4, 5, 6]
        assert minorfunctions.mostCommon(list) == 1

    def emptyTest(self):
        list = []
        assert minorfunctions.mostCommon(list) == None

    def bimodalMidTest(self):
        list = [1, 2, 3, 4, 4, 5, 6, 6, 7]
        assert minorfunctions.mostCommon(list) == 4

    def bimodalEndTest(self):
        list = [1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5]
        assert minorfunctions.mostCommon(list) == 2


mct = MostCommonTester()
mct.allTest()


class reverseArrTester():
    def allTest(self):
        self.emptyTest()
        self.normalTest()
        self.nonExistentAttributeTest()
        self.partExistAttributeTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.reverseArr(list, "yes") == []

    def normalTest(self):
        list = [{"thing": 2, "element": "Absolutely", "Chocolate": "Hot"}, {
            "thing": 14, "element": "Perhaps", "Chocolate": "Dark"}]
        assert minorfunctions.reverseArr(list, "Chocolate") == ["Hot", "Dark"]

    def nonExistentAttributeTest(self):
        list = [{"hi": "ho"}, {"Absolutely": "not"}]
        assert minorfunctions.reverseArr(list, "Clouds") == list

    def partExistAttributeTest(self):
        list = [{"hi": "ho"}, {"Absolutely": "not"}]
        assert minorfunctions.reverseArr(list, "hi") == list


rat = reverseArrTester()
rat.allTest()


class mostCommonLineSpaceTester():
    def allTest(self):
        self.emptyTest()
        self.normalTest()
        self.notLinesTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.mostCommonLineSpace(list) == None

    def normalTest(self):
        list = [{"AftSpace": 15}, {"AftSpace": 12}, {"AftSpace": 15}]
        assert minorfunctions.mostCommonLineSpace(list) == 15

    def notLinesTest(self):
        list = [{"Chocolate": "HotHot"}, {"Chococlate": "Ooo,WeGotIt"}]
        assert minorfunctions.mostCommonLineSpace(list) == None


mclst = mostCommonLineSpaceTester()
mclst.allTest()


class IsInTester():
    def allTest(self):
        self.firstElementTest()
        self.midElementTest()
        self.lastElementTest()
        self.notInTest()
        self.emptyTest()

    def firstElementTest(self):
        list = [1, 2, 3, 4, 5, 6, 8]
        assert minorfunctions.isIn(1, list) == 0

    def midElementTest(self):
        list = [1, 2, 3, 4, 5]
        assert minorfunctions.isIn(3, list) == 2

    def lastElementTest(self):
        list = [1, 2, 3, 4, 5]
        assert minorfunctions.isIn(5, list) == 4

    def notInTest(self):
        list = [1, 2, 3, 4, 5]
        assert minorfunctions.isIn(19, list) == -1

    def emptyTest(self):
        list = []
        assert minorfunctions.isIn(1, list) == -1


iit = IsInTester()
iit.allTest()


class appendNoRepeatsTester():
    def allTest(self):
        self.emptyTest()
        self.appendTest()
        self.excludeRepeatTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.appendNoRepeats(13, list) == [13]

    def appendTest(self):
        list = [1, 2, 3, 4]
        assert minorfunctions.appendNoRepeats(5, list) == [1, 2, 3, 4, 5]

    def excludeRepeatTest(self):
        list = [1, 2, 3, 4]
        assert minorfunctions.appendNoRepeats(4, list) == [1, 2, 3, 4]


anrt = appendNoRepeatsTester()
anrt.allTest()


class myMaxTester():
    def allTest(self):
        self.emptyTest()
        self.indexTest()
        self.nonindexTest()
        self.nonNumberTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.myMax(list) == None

    def indexTest(self):
        list = [1, 2, 3, 4, 5, 4, 3, 2]
        assert minorfunctions.myMax(list, True) == 4

    def nonindexTest(self):
        list = [1, 2, 3, 4, 5, 4, 3, 2]
        assert minorfunctions.myMax(list) == 5

    def nonNumberTest(self):
        list = ["Jace", "the", "Mind", "Sculptor"]
        assert minorfunctions.myMax(list) == "Jace"


mmt = myMaxTester()
mmt.allTest()


class newCoordsTester():
    def allTest(self):
        self.noCoordsTest()
        self.noTypeTest()
        self.normalTest()
        self.addDepthTest()
        self.removeDepthTest()

    def noCoordsTest(self):
        coords = []
        type = 1
        assert minorfunctions.newCoords(coords, type) == [0]

    def noTypeTest(self):
        coords = [1, 2]
        type = 0
        assert minorfunctions.newCoords(coords, type) == [1, 2]

    def normalTest(self):
        coords = [1, 2]
        type = 2
        assert minorfunctions.newCoords(coords, type) == [1, 3]

    def addDepthTest(self):
        coords = [1, 2]
        type = 3
        assert minorfunctions.newCoords(coords, type) == [1, 2, 0]

    def removeDepthTest(self):
        coords = [1, 2]
        type = 1
        assert minorfunctions.newCoords(coords, type) == [2]


nct = newCoordsTester()
nct.allTest()


class limitedSettings():
    def __init__(self, bkmk=0):
        self.bookmark = bkmk


class updateActiveSectionTester():
    def allTest(self):
        self.PDF = PDFfragments.PDFdocument()
        self.pdfSettings = limitedSettings()
        self.words = ["Step", "1.", "Do", "the", "thing", "Step", "2.", "Stop",
                      "doing", "the", "thing", "Step", "2.3", "whatever", "Step", "3.", "Continue", "doing", "the", "thing"]

        self.emptyPDFTest()
        self.emptyWordsTest()
        self.oobBookmarkTest()
        self.normalTest()

    def emptyPDFTest(self):
        assert minorfunctions.updateActiveSection(
            self.PDF, self.pdfSettings, self.words) == None

    def emptyWordsTest(self):
        self.PDF.sections.append(PDFfragments.section("1. Do the thing"))
        self.PDF.sections.append(PDFfragments.section("2. Stop the thing"))
        self.PDF.lastSect().subsections.append(PDFfragments.section("2.3 Whgatever"))
        assert minorfunctions.updateActiveSection(
            self.PDF, self.pdfSettings, []).title == "2.3 Whgatever"

    def oobBookmarkTest(self):
        mark = limitedSettings(500)
        assert minorfunctions.updateActiveSection(
            self.PDF, mark, self.words).title == "2.3 Whgatever"

    def normalTest(self):
        assert minorfunctions.updateActiveSection(
            self.PDF, self.pdfSettings, self.words).title == "2.3 Whgatever"


uast = updateActiveSectionTester()
uast.allTest()


class beginningEqualTester():
    def allTest(self):
        self.trueTest()
        self.falseTest()
        self.emptyTest()

    def emptyTest(self):
        str1 = "Knock, knock, knockin'"
        str2 = ""
        assert minorfunctions.BeginningEqual(str1, str2) == False

    def trueTest(self):
        str1 = "Everytime we touch, I get this feeling..."
        str2 = "Everytime we"
        assert minorfunctions.BeginningEqual(str1, str2) == True

    def falseTest(self):
        str1 = "Cuz everytime we touch, I get this feeling..."
        str2 = "And everytime we kiss, I swear I could fly"
        assert minorfunctions.BeginningEqual(str1, str2) == False


beqt = beginningEqualTester()
beqt.allTest()


class toppestTester():
    def allTest(self):
        self.emptyTest()
        self.normalTest()
        self.topNonNumberTest()
        self.noTopTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.toppest(list) == None

    def noTopTest(self):
        list = [1, 2, 3, 4]
        list2 = [{"Flavor": "Pickle"}, {"Flavor": "Chicken"}]
        assert minorfunctions.toppest(list) == None
        assert minorfunctions.toppest(list2) == None

    def normalTest(self):
        list = [{"top": 123}, {"top": 22}, {"top": 50}]
        assert minorfunctions.toppest(list) == {"top": 22}

    def topNonNumberTest(self):
        list = [{"top": "Alphabet"}, {"top": "alakazam"}]
        assert minorfunctions.toppest(list) == None


tt = toppestTester()
tt.allTest()


class bottomestTester():
    def allTest(self):
        self.emptyTest()
        self.normalTest()
        self.botNonNumberTest()
        self.noBotTest()

    def emptyTest(self):
        list = []
        assert minorfunctions.bottomest(list) == None

    def noBotTest(self):
        list = [1, 2, 3, 4]
        list2 = [{"Flavor": "Pickle"}, {"Flavor": "Chicken"}]
        assert minorfunctions.bottomest(list) == None
        assert minorfunctions.bottomest(list2) == None

    def normalTest(self):
        list = [{"bottom": 123}, {"bottom": 22}, {"bottom": 50}]
        assert minorfunctions.bottomest(list) == {"bottom": 123}

    def botNonNumberTest(self):
        list = [{"bottom": "Alphabet"}, {"bottom": "alakazam"}]
        assert minorfunctions.bottomest(list) == None


bt = bottomestTester()
bt.allTest()


class minLengthTester():
    def allTest(self):
        self.emptyTest()
        self.normalTest()

    def emptyTest(self):
        str1 = ""
        str2 = "hello there"
        assert minorfunctions.minLength(str1, str2) == 0

    def normalTest(self):
        str1 = "1234"
        str2 = "1234567"
        assert minorfunctions.minLength(str1, str2) == 4


mlt = minLengthTester()
mlt.allTest()
