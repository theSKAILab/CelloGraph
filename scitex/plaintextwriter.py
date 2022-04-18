import PDFfragments

# results: screenshot of a textfile

# methods: flow charts of each piece. Make it very black box

# Related works:
# PDF Plumber: Works on PDFs, doesn't do what we want
# ChemDataExtractor: Does what we want, doesn't work on PDFs


# In the motivation section (probably) "Challenges" Slide
# put screenshots of all the complicated parts of PDFs that we need to work with


# PUT LOTS OF PICTURES


# PDF has a list of sections
# PDF also has a list of figure descriptions/captions and table descriptions/captions

# each section has a list of paragraphs and a list of subsections
# each section's paragraphs are only the paragraphs between that section and the next subsection

# each paragraph has a list of sentences.

# each sentence is a string.


def SectiontoPlain(sec):
    retval = ""

    retval += "\n\nSection " + ": " + sec.title
    for i in range(len(sec.para)):
        retval += sec.para[i].gettext()

    for s in range(len(sec.subsections)):
        retval += SectiontoPlain(sec.subsections[i])
    return retval


def PDFtoPlain(PDF):
    retval = ""

    for sec in range(len(PDF.sections)):
        retval += SectiontoPlain(PDF.sections[sec])

    for fig in range(len(PDF.figures)):
        retval += "\nFigure " + fig + " description: " + PDF.figures[fig]

    for tab in range(len(PDF.tables)):
        retval += "\nTable " + tab + " description: " + PDF.tables[tab]

    return retval
