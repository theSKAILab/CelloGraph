from enum import Enum

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
    def __init__(self, d, diffs, lineheight, lineratio, error, consistentRatio=0):
        self.size = lineSize()
        self.befspace = spaceSize()
        self.aftspace = spaceSize()
        self.type = diffType()
        self.consistentRatio = consistentRatio
        self.calcBasicSet(d, diffs, lineheight, error)
        self.calcAdvSet(d, diffs, lineratio)

    def calcBasicSet(self, d, diffs, lineheight, error):
        # diff is the difference between top of this line and bottom of previous line
        # ratio is the height/space ratio
        # height is how tall this line is.
        diff = diffs[1][d]
        ratio = diffs[2][d]
        height = diffs[3][d]

        # Figure out a bunch of stuff
        # need d, lineheight, diffs

        # is the text big
        self.size = lineSize()
        if(height > lineheight + error):
            self.size = lineSize().BIG_SIZE
        elif(height < lineheight - error):
            self.size = lineSize().SMALL_SIZE
        else:
            self.size = lineSize().NORMAL_SIZE

        # is there a big space beforehand
        self.befspace = spaceSize()
        if(d != 0):
            if(diffs[1][d-1] > linespace + error):
                self.befspace = spaceSize().BIG_SPACE
            elif(diffs[1][d-1] < linespace - error):
                self.befspace = spaceSize().SMALL_SPACE
            else:
                self.befspace = spaceSize().NORMAL_SPACE
        else:
            self.befspace = spaceSize().BIG_SPACE

        # is there a big space afterwards
        self.aftspace = spaceSize()
        if(diffs[1][d] > linespace + error):
            self.aftspace = spaceSize().BIG_SPACE
        elif(diffs[1][d] < linespace - error):
            self.aftspace = spaceSize().SMALL_SPACE
        else:
            self.aftspace = spaceSize().NORMAL_SPACE

    def calcAdvSet(self, d, diffs, lineratio):
        # if we're in a multiline section then figure out whether it's ending.
        if(self.consistentRatio != 0):
            if(d < len(diffs[1])-1 and diffs[2][d] == consistentRatio and diffs[2][d+1] != lineratio):
                self.type = diffType().IN_MULTI
            else:
                self.type = diffType.END_SECTION
        # if the next line is similar to this line and not normal text, it's a multiline section.
        elif(d < len(diffs[1])-1 and self.befspace == spaceSize.BIG_SPACE and diffs[2][d+1] == ratio and not diffs[2][d+1] == lineratio):
            self.type = diffType().START_MULTI
        # if there's a ton of space before and after this, it's a single line section.
        elif(self.aftspace == spaceSize().BIG_SPACE and self.befspace == spaceSize().BIG_SPACE):
            self.type = diffType.END_SECTION
        # if there's a big space but normal text, then it's the end of a block, which we do want to detect.
        elif(self.aftspace == spaceSize().BIG_SPACE):
            self.type = diffType().END_BLOCK
        # if it's none of those, it's normal text.
        else:
            self.type = diffType().NORMAL_TEXT
            self.consistentRatio = 0
