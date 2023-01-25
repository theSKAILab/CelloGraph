import grobidStuff
import altoStuff

groStrings = grobidStuff.grobidWords("scitex/grobidAltoStuff/HeinzeGrobid.xml")
altoStrings, altoWords, subFonts, superFonts = altoStuff.AltoLists("scitex/grobidAltoStuff/HeinzeAlto.xml")

subs = []
supers = []

subStrings = []
superStrings = []

#just go through the words in altStrings until we get like, 5 in a row that match with groStrings.
altDex, groDex = altoStuff.sync(groStrings, altoStrings, checkSize=400)

while altDex < len(altoStrings)-1 and groDex<len(groStrings)-1:
    altoW, altoFullW, groW = altoStrings[altDex], altoWords[altDex], groStrings[groDex]

    if(altoW == groW):
        
        #if it's not script we don't care, if it is, make a note
        script = altoStuff.isScript(altoWords[altDex], superFonts, subFonts)
        if(not script):
            altDex += 1
            groDex += 1
            continue
        elif(script == "super"):
            supers.append([groDex, groW])
            superStrings.append(groW)
        elif(script == "sub"):
            subs.append([groDex, groW])
            subStrings.append(groW)
        
        altDex += 1
        groDex += 1

    else:
        altDex, groDex = altoStuff.sync(groStrings, altoStrings, altDex, groDex)
    


fixedBody = grobidStuff.addScript("scitex/grobidAltoStuff/HeinzeGrobid.xml", supers, subs)

outputXML = grobidStuff.rebuild("scitex/grobidAltoStuff/HeinzeGrobid.xml", fixedBody)

print("hi")

#results of checking stuff out
    #1. there's not an option to have Grobid use something other than UTF-8
    #2. there is also not an option for pdfalto to use non-UTF-8 encoding