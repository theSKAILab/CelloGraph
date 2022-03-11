# MINOR FUNCTIONS
# The following functions are short and used for my own sanity


# returns the most common element in an array.
# if there's a tie it'll take the one that happens first.
# index is something for whether you want the index or the value.
def mostCommon(arr, index=False):
    retval = 0

    # countarr has elements [element, indices, counts]
    countarr = [[], [], []]

    for i in range(len(arr)):
        j = isIn(arr[i], countarr[0])
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


# Python's default 'in' method doens't return the index, so I fixed that.
def isIn(element, arr):
    for i in range(len(arr)):
        if arr[i] == element:
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
