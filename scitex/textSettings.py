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


class diffType(Enum):
    END_SECTION = 1
    END_BLOCK = 2
    START_MULTI = 3
    IN_MULTI = 4
    FIGURE_TEXT = 5
    NORMAL_TEXT = 6


# class describing what kind of text line we're dealing with.
# takes a bunch of inputs, and then uses them to calibrate itself.
class diffSettings:
    def __init__(self, d, diffs, pdfSettings, error, consistentRatio=0):
        self.size = lineSize.NORMAL_SIZE
        self.befspace = spaceSize.NORMAL_SPACE
        self.aftspace = spaceSize.NORMAL_SPACE
        self.type = diffType.NORMAL_TEXT
        self.consistentRatio = pdfSettings.consistentRatio
        self.calcBasicSet(d, diffs, pdfSettings, error)
        self.calcAdvSet(d, diffs, pdfSettings, error)

    def calcBasicSet(self, d, diffs, pdfSettings, error):

        befSpace = diffs[d]["BefSpace"]
        aftSpace = diffs[d]["AftSpace"]
        height = diffs[d]["Height"]

        # is the text big
        if(minorfunctions.isGreater(height, pdfSettings.lineheight, error)):
            self.size = lineSize.BIG_SIZE
        elif(minorfunctions.isLesser(height, pdfSettings.lineheight, error)):
            self.size = lineSize.SMALL_SIZE
        else:
            self.size = lineSize.NORMAL_SIZE

        # is there a big space beforehand
        if(d != 0):
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

    def calcAdvSet(self, d, diffs, pdfSettings, error):

        if(self.InMultiTest(d, diffs, pdfSettings, error)):
            self.type = diffType.IN_MULTI

        elif(self.StartMultiTest(d, diffs, pdfSettings, error)):
            self.type = diffType.START_MULTI

        elif(self.aftspace == spaceSize.BIG_SPACE and self.befspace == spaceSize.BIG_SPACE):
            self.type = diffType.END_SECTION

        elif(self.aftspace == spaceSize.BIG_SPACE):
            self.type = diffType.END_BLOCK

        else:
            self.type = diffType.NORMAL_TEXT
            self.consistentRatio = 0

    # if we're not at the bottom of the col and there's a big space before this line and there's a big space after this line and next line.
    def StartMultiTest(self, d, diffs, pdfSettings, error):
        if(minorfunctions.EndofCol(d+1, diffs)):
            return False
        if(minorfunctions.areEqual(diffs[d+1]["AftRatio"], pdfSettings.lineratio, error)):
            return False
        if(minorfunctions.areEqual(diffs[d+1]["BefRatio"], pdfSettings.lineratio, error)):
            return False
        if(not (self.befspace == spaceSize.BIG_SPACE and self.aftspace == spaceSize.BIG_SPACE)):
            return False
        if(d == 0):
            if(minorfunctions.areEqual(diffs[d+1]["AftSpace"], diffs[d]["AftSpace"], error)):
                return True
        if(d != 0):
            return minorfunctions.isLesser(diffs[d]["AftSpace"], diffs[d]["BefSpace"], error)

    # if we're not at the bottom of the col and the ratio of size to spacing is the same for the next line as it is for this line,
        # and that ratio isn't the same as the normal text ratio.
    def InMultiTest(self, d, diffs, pdfSettings, error):
        if(d == 0):
            return False
        if(minorfunctions.EndofCol(d+1, diffs) or self.consistentRatio == 0):
            return False
        if(minorfunctions.areEqual(diffs[d+1]["AftRatio"], pdfSettings.lineratio, error)):
            return False
        if(minorfunctions.areEqual(diffs[d]["AftRatio"], self.consistentRatio, error)):
            return True
