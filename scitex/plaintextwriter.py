import PDFfragments
import minorfunctions

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
        p = sec.para[i]
        retval += "\n\nNEW PARA: (Start: pg " + \
            str(p.startPage) + ", col " + str(p.startCol+1)
        retval += "; End: pg " + str(p.endPage) + \
            ", col " + str(p.endCol+1) + ")"
        for j in range(len(sec.para[i].sentences)):
            s = p.sentences[j]
            retval += "\n\tNEW SENTENCE: (Start: pg " + \
                str(s.startPage) + ", col " + str(s.startCol+1)
            retval += "; End: pg " + \
                str(s.endPage) + ", col " + str(s.endCol+1) + ")" + s.text

    for i in range(len(sec.subsections)):
        retval += SectiontoPlain(sec.subsections[i])
    return retval


def PDFtoPlain(PDF, times=[]):
    retval = ""

    if(times):
        retval += "\nAll Times:"
        for t in range(len(times)):
            retval += "\nPage " + str(t+1) + ": " + str(times[t])
        times = minorfunctions.bubbleSort(times)
        retval += "\n\n\nMedian Time per page = " + \
            str(times[int(len(times)/2)])
        retval += "\nAvg Time per page = " + str(sum(times)/len(times))

    for sec in range(len(PDF.sections)):
        retval += SectiontoPlain(PDF.sections[sec])

    retval += "\n\n\n"
    for fig in range(len(PDF.figures)):
        retval += FiguretoPlain(PDF.figures[fig])

    for tab in range(len(PDF.tables)):
        retval += "\n\n\n"
        retval += TabletoPlain(PDF.tables[tab])

    return retval


def FiguretoPlain(figure):
    retval = "\n\n"
    retval += figure.text

    return retval


def TabletoPlain(Table):

    retval = "NEW TABLE: Page " + str(Table[1])

    Table = Table[0]
    for row in range(len(Table)):
        retval += "\n--------------------------\n"
        for cell in range(len(Table[row])):
            retval += "|"
            for word in range(len(Table[row][cell])):
                retval += Table[row][cell][word]["text"]
                retval += " "

    return retval
