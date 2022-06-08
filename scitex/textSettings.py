from enum import Enum
import minorfunctions

# An enum describing the size of text


class lineSize(Enum):
    NORMAL_SIZE = 1
    BIG_SIZE = 2
    SMALL_SIZE = 3

# An enum describing the amount of space before/after a line of text


class spaceSize(Enum):
    NORMAL_SPACE = 1
    BIG_SPACE = 2
    SMALL_SPACE = 3

# An enum describing the types of lines of text.


class lineType(Enum):
    END_SECTION = 1
    END_BLOCK = 2
    START_MULTI = 3
    IN_MULTI = 4
    FIGURE_TEXT = 5
    NORMAL_TEXT = 6


# class describing what kind of text line we're dealing with.
# takes a bunch of inputs, and then uses them to calibrate itself.
class lineSettings:
    def __init__(self, i, lines, pdfSettings, error, consistentRatio=0):
        self.size = lineSize.NORMAL_SIZE
        self.befspace = spaceSize.NORMAL_SPACE
        self.aftspace = spaceSize.NORMAL_SPACE
        self.type = lineType.NORMAL_TEXT
        self.consistentRatio = pdfSettings.consistentRatio
        self.calcBasicSet(i, lines, pdfSettings, error)
        self.calcAdvSet(i, lines, pdfSettings, error)

    def calcBasicSet(self, i, lines, pdfSettings, error):

        befSpace = lines[i]["BefSpace"]
        aftSpace = lines[i]["AftSpace"]
        height = lines[i]["Height"]

        # is the text big
        if(minorfunctions.isGreater(height, pdfSettings.lineheight, error)):
            self.size = lineSize.BIG_SIZE
        elif(minorfunctions.isLesser(height, pdfSettings.lineheight, error)):
            self.size = lineSize.SMALL_SIZE
        else:
            self.size = lineSize.NORMAL_SIZE

        # is there a big space beforehand
        if(i != 0):
            if(minorfunctions.isGreater(befSpace, pdfSettings.linespace, error)):
                self.befspace = spaceSize.BIG_SPACE
            elif(minorfunctions.isLesser(befSpace, pdfSettings.linespace, error)):
                self.befspace = spaceSize.SMALL_SPACE
            else:
                self.befspace = spaceSize.NORMAL_SPACE
        else:
            self.befspace = spaceSize.BIG_SPACE

        # is there a big space afterwards
        if(minorfunctions.isGreater(aftSpace, pdfSettings.linespace, error)):
            self.aftspace = spaceSize.BIG_SPACE
        elif(minorfunctions.isLesser(aftSpace, pdfSettings.linespace, error)):
            self.aftspace = spaceSize.SMALL_SPACE
        else:
            self.aftspace = spaceSize.NORMAL_SPACE

    def calcAdvSet(self, i, lines, pdfSettings, error):
        if(self.InMultiTest(i, lines, pdfSettings, error)):
            self.type = lineType.IN_MULTI

        elif(self.StartMultiTest(i, lines, pdfSettings, error)):
            self.type = lineType.START_MULTI

        elif(self.EndSectionTest(i, lines, pdfSettings, error)):
            self.type = lineType.END_SECTION

        elif(self.aftspace == spaceSize.BIG_SPACE):
            self.type = lineType.END_BLOCK

        else:
            self.type = lineType.NORMAL_TEXT
            self.consistentRatio = 0

    # if we're not at the bottom of the col and there's a big space before this line and there's a big space after this line and next line.
    def StartMultiTest(self, i, lines, pdfSettings, error):
        if(minorfunctions.isEndofCol(i+2, lines)):
            return False
        if(not minorfunctions.areEqual(lines[i]["AftSpace"], lines[i+1]["AftSpace"], error)):
            return False
        if(minorfunctions.areEqual(lines[i+1]["AftRatio"], pdfSettings.lineratio, error)):
            return False
        if(minorfunctions.areEqual(lines[i+1]["BefRatio"], pdfSettings.lineratio, error)):
            return False
        if(not (self.befspace == spaceSize.BIG_SPACE and self.aftspace == spaceSize.BIG_SPACE)):
            return False
        if(minorfunctions.areEqual(lines[i]["BefSpace"], pdfSettings.linespace, error) or minorfunctions.areEqual(lines[i]["AftSpace"], pdfSettings.linespace, error)):
            return False
        if(minorfunctions.isGreater(lines[i]["Height"], lines[i+1]["Height"], error)):
            return False
        if(i == 0):
            if(minorfunctions.areEqual(lines[i+1]["AftSpace"], lines[i]["AftSpace"], pdfSettings.interline)):
                return True
        if(i != 0):
            if(minorfunctions.isLesser(lines[i]["AftSpace"], lines[i]["BefSpace"], pdfSettings.interline)):
                return True
        return False

    # if we're not at the bottom of the col and the ratio of size to spacing is the same for the next line as it is for this line,
    # and that ratio isn't the same as the normal text ratio.

    def InMultiTest(self, i, lines, pdfSettings, error):
        if(i == 0):
            return False
        if(minorfunctions.isEndofCol(i+1, lines) or self.consistentRatio == 0):
            return False
        if(minorfunctions.areEqual(lines[i]["BefSpace"], pdfSettings.linespace, error) or minorfunctions.areEqual(lines[i]["AftSpace"], pdfSettings.linespace, error)):
            return False
        if(minorfunctions.areEqual(lines[i+1]["AftRatio"], pdfSettings.lineratio, error)):
            return False
        if(minorfunctions.areEqual(lines[i]["AftRatio"], self.consistentRatio, error)):
            return True

    def EndSectionTest(self, i, lines, pdfSettings, error):
        if(i == len(lines)-1):
            return False
        return self.aftspace == spaceSize.BIG_SPACE and self.befspace == spaceSize.BIG_SPACE
