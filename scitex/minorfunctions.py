import textprocessing


from collections import Counter


def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


# MINOR FUNCTIONS
# The following functions are short and used for my own sanity


# "equal" so that we can have an error margin, error is a percentage
def areEqual(val1, val2, error=0):
    val1 = float(val1)
    val2 = float(val2)
    if(val1 <= val2*((error+100)/100) and val1 >= val2*((100-error)/100)):
        return True
    else:
        return False


# areEqual but for a list.


def listElementsEqual(list, error=0):
    for i in range(len(list)):
        for j in range(1, len(list)):
            if(not areEqual(list[i], list[j], error)):
                return False
    return True


def isGreater(val1, val2, error=0):
    val1 = float(val1)
    val2 = float(val2)
    if(val1 > val2*((100+error)/100)):
        return True
    else:
        return False


def isLesser(val1, val2, error=0):
    val1 = float(val1)
    val2 = float(val2)
    if(val1 < val2*((100-error)/100)):
        return True
    else:
        return False


def EndofCol(d, diffs):
    return d > len(diffs)-1

# returns the most common element in an array.
# if there's a tie it'll take the one that happens first.
# index is something for whether you want the index or the value.


def mostCommon(arr, index=False, error=0):
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
def reverseDiff(diffs, attribute):
    retval = []
    for d in range(len(diffs)):
        retval.append(diffs[d][attribute])
    return retval


def mostCommonLineSpace(arr, index=False, error=0):
    retval = 0

    arr = reverseDiff(arr, "AftSpace")

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
    #occurence_count = Counter(arr)
#
    # if(index):
    #    mostcommon = occurence_count.most_common(1)[0][0]
    #    for i in range(len(arr)):
    #        if(areEqual(arr[i], mostcommon, error)):
    #            return i
    #    return arr[0]
    # else:
    #    # returns the thing with the highest count
    #    return occurence_count.most_common(1)[0][0]


# Python's default 'in' method doens't return the index, so I fixed that.
def isIn(element, arr, error=0):
    for i in range(len(arr)):
        if areEqual(arr[i], element, error):
            return i
    return -1

# similarly, python's default 'max' function doesn't return the index.
# so I made a new max, where index=True will return the index.


def myMax(arr, index=False):
    retval = 0
    for i in range(len(arr)):
        if arr[i] > arr[retval]:
            retval = i
    if(index):
        return retval
    else:
        return arr[retval]


# update the coordinates
def newCoords(coords, type):
    newcoords = []
    # if we're in a shallower section now (from 2.3.4.5 to 3.1) remove depth
    if(len(coords) > type):
        for i in range(type):
            newcoords.append(coords[i])
    # if we're in a deeper section, add depth.
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


def updateActiveSection(PDF, words, pdfSettings):
    active = PDF.lastSect()
    test = active.lastsub()
    while(test != (None, None)):
        active = test[0]
        test = active.lastsub()

    active.type = textprocessing.FindsectionType(
        words[pdfSettings.bookmark])
    return active
