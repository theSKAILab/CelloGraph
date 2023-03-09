import main

HGpath = "scitex/grobidAltoStuff/grobid/HeinzeGrobid.xml"
HApath = "scitex/grobidAltoStuff/pdfalto/HeinzeAlto.xml"
HOpath = "scitex/grobidAltoStuff/scitex/HeinzeOutput.xml"
Heinze = [HGpath, HApath, HOpath]

GGpath = "scitex/grobidAltoStuff/grobid/GuptaGrobid.xml"
GApath = "scitex/grobidAltoStuff/pdfalto/GuptaAlto.xml"
GOpath = "scitex/grobidAltoStuff/scitex/GuptaOutput.xml"
Gupta = [GGpath, GApath, GOpath]

KGpath = "scitex/grobidAltoStuff/grobid/KlemmGrobid.xml"
KApath = "scitex/grobidAltoStuff/pdfalto/KlemmAlto.xml"
KOpath = "scitex/grobidAltoStuff/scitex/KlemmOutput.xml"
Klemm = [KGpath, KApath, KOpath]

SGpath = "scitex/grobidAltoStuff/grobid/ShiGrobid.xml"
SApath = "scitex/grobidAltoStuff/pdfalto/ShiAlto.xml"
SOpath = "scitex/grobidAltoStuff/scitex/ShiOutput.xml"
Shi = [SGpath, SApath, SOpath]


def test(arr):
    main.addScript(arr[0], arr[1], arr[2])


def testAll():
    test(Heinze)
    test(Gupta)
    test(Klemm)
    test(Shi)

testAll()