import textprocessing


from collections import Counter


def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


# MINOR FUNCTIONS
# The following functions are short and used for my own sanity


# if percentage is true, it'll return true if v1 is within error% of v2
# if percentage is false, it'll return true if v1 = v2 +- error
def areEqual(val1, val2, error=0, percentage=False):
    val1 = float(val1)
    val2 = float(val2)
    error = float(error)
    if(percentage):
        if(val1 < val2*((100+error)/100) and val1 > val2*(100-error)/100):
            return True
        else:
            return False
    else:
        if(val1 <= val2 + error and val1 >= val2 - error):
            return True
        else:
            return False


# areEqual but for a list.
def listElementsEqual(list, error=0, percentage=False):
    for i in range(len(list)):
        for j in range(i, len(list)):
            if(not areEqual(list[i], list[j], error, percentage)):
                return False
    return True


def bubbleSort(arr):
    if(len(arr) < 2):
        return arr

    swapped = True
    while swapped:
        swapped = False
        for i in range(1, len(arr)):
            if arr[i-1] < arr[i]:
                swapped = True
                arr[i], arr[i - 1] = arr[i - 1], arr[i]

    return arr

# sorts a 2d array by length, so that the longest is first
# I just use bubble sort for now


def sortByLen(arr):
    if(len(arr) < 2):
        return arr

    swapped = True
    while swapped:
        swapped = False
        for i in range(1, len(arr)):
            if len(arr[i-1].text) < len(arr[i].text):
                swapped = True
                arr[i], arr[i - 1] = arr[i - 1], arr[i]

    return arr

# returns true if val1 > val2+error or val1 < val2* (100+error)%


def isGreater(val1, val2, error=0, percentage=False):
    val1 = float(val1)
    val2 = float(val2)
    error = float(error)
    if(percentage):
        if(val1 > val2*((100+error)/100)):
            return True
        else:
            return False
    else:
        if(val1 > val2 + error):
            return True
        else:
            return False


# returns true if val1 < val2-error or val1 < val2* (100-error)%
def isLesser(val1, val2, error=0, percentage=False):
    val1 = float(val1)
    val2 = float(val2)
    error = float(error)
    if(percentage):
        if(val1 < val2*((100-error)/100)):
            return True
        else:
            return False
    else:
        if(val1 < val2 - error):
            return True
        else:
            return False


# just for shorthand
def isEndofCol(i, lines):
    return i >= len(lines)-1 or lines[i]["AftSpace"] < 0


# returns the most common element in an array.
# if there's a tie it'll take the one that happens first.
# index is something for whether you want the index or the value.
def mostCommon(arr, index=False, error=0):
    if(len(arr) == 0):
        return None
    retval = 0

    # countarr has elements [element, indices, counts]
    countarr = [[], [], []]

    for i in range(len(arr)):
        j = isIn(arr[i], countarr[0], error)
        if(j > -1):
            countarr[2][j] += 1
        else:
            countarr[0].append(arr[i])
            countarr[1].append(i)
            countarr[2].append(1)

    maxdex = myMax(countarr[2], True)
    if(index):
        # returns the index of the thing with the highest count
        return countarr[1][maxdex]
    else:
        # returns the thing with the highest count
        return countarr[0][maxdex]


# take a list of dicts, make a list of attribute
def reverseArr(arr, attribute):
    retval = []
    for i in range(len(arr)):
        try:
            arr[i][attribute]
        except:
            return arr
        retval.append(arr[i][attribute])
    return retval


# this is for shorthand.
def mostCommonLineSpace(arr, index=False, error=0):
    if(len(arr) == 0):
        return None
    try:
        arr[0]["AftSpace"]
    except:
        return None

    arr = reverseArr(arr, "AftSpace")
    return mostCommon(arr, index, error)


# Python's default 'in' method doens't return the index, so I fixed that.
def isIn(element, arr, error=0, percentage=False):
    for i in range(len(arr)):
        if areEqual(arr[i], element, error, percentage):
            return i
    return -1


# if element isn't in arr, appends element to arr.
# takes a list, returns a list.
def appendNoRepeats(element, arr):
    inArr = False
    for i in range(len(arr)):
        test = arr[i]
        if arr[i] == element:
            inArr = True
            break
    if inArr == False:
        arr.append(element)
    return arr


# I made a new max function, where index=True will return the index of the max.
def myMax(arr, index=False):
    if(len(arr) == 0):
        return None

    retval = 0
    for i in range(len(arr)):
        try:
            test = int(arr[i])
        except:
            return arr[0]
        if arr[i] > arr[retval]:
            retval = i
    if(index):
        return retval
    else:
        return arr[retval]


# update the coordinates of what section or sub-sub-etc-section we're in.
def newCoords(coords, type):
    if(coords == []):
        return [0]
    if(type == 0):
        return coords
    newcoords = []
    # if we're in a shallower section now (from 2.3.4.5 to 2.4) remove depth
    if(len(coords) > type):
        for i in range(type):
            newcoords.append(coords[i])
    # if we're in a deeper section, (2.3 to 2.3.1) add depth.
    elif(len(coords) < type):
        newcoords = coords
        newcoords.append(-1)
    # else just copy as is
    else:
        newcoords = coords
    # update coords
    coords = newcoords
    if(coords == []):
        return [0]
    else:
        coords[len(coords)-1] += 1
        return coords


# I wanted an xor for something and was sad that python didn't have one
def xor(a, b):
    return not(a and b) and not(not a and not b)


# turn a string of text into an array of words
def words(str):
    retval = []
    bookmark = 0
    for i in range(len(str)):
        if str[i] == ' ' or str[i] == '.':
            retval.append(str[bookmark:i])
            bookmark = i+1
    if(bookmark < len(str)-1):
        retval.append(str[bookmark:])
    return retval

# returns the last subsection (or sub-sub-sub-etc-section) of the last section
# also updates its type if need be.


def updateActiveSection(PDF, words, pdfSettings):
    if(len(PDF.sections) == 0):
        return None
    active = PDF.lastSect()
    if(active.title != ""):
        test = active.lastsub()
        if(test[0]):
            active = test[0]
        while(active.lastsub() != (None, None)):
            active = test[0]
            test = active.lastsub()

        # if(pdfSettings.bookmark < len(words)):
        #    active.type = textprocessing.FindsectionType(
        #        words[pdfSettings.bookmark])
        # else:
        #    active.type = textprocessing.FindsectionType(active.title)
    return active


# returns either "None" if there are no lines, or the highest line.
# pass in pdf.pages[i].objs
def heighestLine(objs):
    try:
        objs["line"]
    except:
        return None

    return toppest(objs["line"])


# returns either "None" if there are no lines, or the lowest line.
# pass in pdf.pages[i].objs
def lowestLine(objs):
    try:
        objs["line"]
    except:
        return None

    return bottomest(objs["line"])


# returns the thing with the highest "top" attribute
def toppest(list):
    if(len(list) == 0):
        return None
    retval = None
    for thing in list:
        try:
            thing["top"]
            test = int(thing["top"])
        except:
            return None
        if(not retval):
            retval = thing
        elif(thing["top"] < retval["top"]):
            retval = thing
    return retval


# returns the thing with the lowest "bottom" attribute
def bottomest(list):
    if(len(list) == 0):
        return None
    retval = None
    for thing in list:
        try:
            thing["bottom"]
            test = int(thing["bottom"])
        except:
            return None
        if(not retval):
            retval = thing
        elif(thing["bottom"] > retval["bottom"]):
            retval = thing
    return retval


def BeginningEqual(str1, str2):
    if(len(str1) == 0 or len(str2) == 0):
        return False
    length = minLength(str1, str2)
    if str1[:length] == str2[:length]:
        return True
    return False


def EndEqual(str1, str2):
    if(len(str1) == 0 or len(str2) == 0):
        return False
    length = minLength(str1, str2)
    mini1 = str1[len(str1)-length:]
    mini2 = str2[len(str2)-length:]
    if mini1 == mini2:
        return True
    return False


def minLength(str1, str2):
    if(len(str1) > len(str2)):
        return len(str2)
    else:
        return len(str1)

# really long if statement


def isCaption(str):
    if(str == "Fig." or "Figure"):
        return True
    if(str == "Tab." or "Table"):
        return True
    if(str == "Scheme" or "Schema"):
        return True
    if(str == "Graph" or "Graphic"):
        return True
    return False


# returns true if its a space or a wacky character that ends up looking like a space.
def isSpace(chars, i):
    if(i == 0 or i > len(chars)-1):
        return False
    if(chars[i]["text"] == ' ' or chars[i]["text"] == '\xa0'):
        return True
    return False
