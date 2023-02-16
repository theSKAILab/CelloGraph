import grobidStuff
import altoStuff
import tryingDiff

groStrings = grobidStuff.strWords("scitex/grobidAltoStuff/HeinzeGrobid.xml")
altoStrings, altoWords, subFonts, superFonts = altoStuff.AltoLists("scitex/grobidAltoStuff/HeinzeAlto.xml")

matches = tryingDiff.getMatches(groStrings, altoStrings)

subs = []
supers = []

subStrings = []
superStrings = []
matchesWords = []

totalLost = 0
prev = 0
biggestGap = [0, 0]

for match in matches:
    lost = match[1]-prev
    if(lost > biggestGap[0]):
        biggestGap[0] = lost
        biggestGap[1] = match[1]

    totalLost += lost
    prev = match[0]+match[2]
    
    matchesWords.append([match[1], match[2], groStrings[match[1]:match[1]+match[2]], match[0], altoStrings[match[0]:match[0]+match[2]]])

for match in matches:
    altDex, groDex, matchLen = match
    for i in range(matchLen):
        altoW = altoStrings[altDex+i]
        groW = groStrings[groDex+i]


        script = altoStuff.isScript(altoWords[altDex+i], superFonts, subFonts)
        if(script == "super"):
            supers.append([groDex+i, groStrings[groDex+i]])
            superStrings.append(groStrings[groDex+i])
        if(script == "sub"):
            subs.append([groDex+i, groStrings[groDex+i]])
            subStrings.append(groStrings[groDex+i])

    



#just go through the words in altStrings until we get like, 5 in a row that match with groStrings.
#groDex, altDex = altoStuff.sync(groStrings, altoStrings, checkSize=400)

#while altDex < len(altoStrings)-1 and groDex<len(groStrings)-1:
#    altoW, altoFullW, groW = altoStrings[altDex], altoWords[altDex], groStrings[groDex]

#   contextAlt = altoStrings[altDex-5:altDex+6]
#    contextGro = groStrings[groDex-5:groDex+6]


#    if(altoW == groW):

        
        #if it's not script we don't care, if it is, make a note
#        script = altoStuff.isScript(altoWords[altDex], superFonts, subFonts)
#        if(not script):
#            altDex += 1
#            groDex += 1
#            continue
#        elif(script == "super"):
#            supers.append([groDex, groW])
#            superStrings.append(groW)
#        elif(script == "sub"):
#            subs.append([groDex, groW])
#            subStrings.append(groW)
        
#        altDex += 1
#        groDex += 1

#    else:
#        skipGro, skipAlt = altoStuff.sync(groStrings, altoStrings, altDex, groDex)
#        if skipAlt == 0 and skipGro == 0:
#            skipAlt = 1
#            if(altDex > 2000):
#                print("hey wait a minute")
#        altDex += skipAlt
#        groDex += skipGro
    

groLongStr = grobidStuff.longStr("scitex/grobidAltoStuff/HeinzeGrobid.xml")

#fixedBody = grobidStuff.addScript("scitex/grobidAltoStuff/HeinzeGrobid.xml", supers, subs)

#outputXML = grobidStuff.rebuild("scitex/grobidAltoStuff/HeinzeGrobid.xml", fixedBody)

outputXML = grobidStuff.rebuild("scitex/grobidAltoStuff/HeinzeGrobid.xml", groLongStr, supers, subs)

print("hi")

#results of checking stuff out
    #1. there's not an option to have Grobid use something other than UTF-8
    #2. there is also not an option for pdfalto to use non-UTF-8 encoding