import PDFfragments

# Related works:
# PDF Plumber: Works on PDFs, doesn't do what we want
# ChemDataExtractor: Does what we want, doesn't work on PDFs

# PDF has a list of sections
# PDF also has a list of figure descriptions/captions and table descriptions/captions

# each section has a list of paragraphs and a list of subsections
# each section's paragraphs are only the paragraphs between that section and the next subsection

# each paragraph has a list of sentences.

# each sentence is a string.


def SectiontoPlain(sec):
    retval = ""

    retval += "\n\nNEW SECTION: " + sec.title + \
        " (Level: " + str(sec.type) + ")\n"
    for i in range(len(sec.para)):
        retval += "\n\nNEW PARA:"
        for j in range(len(sec.para[i].sentences)):
            retval += "\n\tNEW SENTENCE: " + sec.para[i].sentences[j].text

    for i in range(len(sec.subsections)):
        retval += SectiontoPlain(sec.subsections[i])
    return retval


def PDFtoPlain(PDF):
    retval = ""

    for sec in range(len(PDF.sections)):
        retval += SectiontoPlain(PDF.sections[sec])

    retval += "\n\n\n"
    for fig in range(len(PDF.figures)):
        retval += FiguretoPlain(PDF.figures[fig])

    for tab in range(len(PDF.tables)):
        retval += "\n\n\n"
        #retval += TabletoPlain(PDF.tables[tab])

    return retval


def FiguretoPlain(figure):
    retval = "\n\n"
    for line in range(len(figure)):
        retval += "\n"
        for word in range(len(figure[line]["Text"])):
            retval += figure[line]["Text"][word]["text"]
            retval += " "

    return retval


def TabletoPlain(Table):
    retval = ""
    for line in range(len(figure)):
        retval += "\n"
        for word in range(len(figure[line]["Text"])):
            retval += figure[line]["Text"][word]["text"]
            retval += " "

    return retval
