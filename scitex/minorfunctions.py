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


# returns true if val1 > val2+error or val1 < val2* (100+error)%
def isGreater(val1, val2, error=0, percentage=False):
    val1 = float(val1)
    val2 = float(val2)
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
    return i > len(lines)-1


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
        retval.append(arr[i][attribute])
    return retval


# this is for shorthand.
def mostCommonLineSpace(arr, index=False, error=0):
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
        if arr[i] == element:
            inArr = True
            break
    if inArr == False:
        arr.append(element)
    return arr


# I made a new max function, where index=True will return the index of the max.
def myMax(arr, index=False):
    retval = 0
    for i in range(len(arr)):
        if arr[i] > arr[retval]:
            retval = i
    if(index):
        return retval
    else:
        return arr[retval]


# update the coordinates of what section or sub-sub-etc-section we're in.
def newCoords(coords, type):
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
    coords[len(coords)-1] += 1
    return coords


# returns the last subsection (or sub-sub-sub-etc-section) of the last section
# also updates its type if need be.
def updateActiveSection(PDF, words, pdfSettings):
    active = PDF.lastSect()
    test = active.lastsub()
    while(test != (None, None)):
        active = test[0]
        test = active.lastsub()

    active.type = textprocessing.FindsectionType(
        words[pdfSettings.bookmark])
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
    retval = None
    for thing in list:
        if(not retval):
            retval = thing
        elif(thing["top"] > retval["top"]):
            retval = thing
    return retval


# returns the thing with the lowest "bottom" attribute
def bottomest(list):
    retval = None
    for thing in list:
        if(not retval):
            retval = thing
        elif(thing["bottom"] < retval["bottom"]):
            retval = thing
    return retval
