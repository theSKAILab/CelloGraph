import grobidStuff
import altoStuff
import tryingDiff

groStrings = grobidStuff.grobidWords("scitex/grobidAltoStuff/HeinzeGrobid.xml")
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

        

groLongStr = grobidStuff.longStr("scitex/grobidAltoStuff/HeinzeGrobid.xml")

#fixedBody = grobidStuff.addScript("scitex/grobidAltoStuff/HeinzeGrobid.xml", supers, subs)

#outputXML = grobidStuff.rebuild("scitex/grobidAltoStuff/HeinzeGrobid.xml", fixedBody)

outputXML = grobidStuff.rebuild("scitex/grobidAltoStuff/output.xml", groLongStr, supers, subs)

print("hi")