import PDFfragments
import minorfunctions

# Related works:
# PDF Plumber: Works on PDFs, doesn't do what we want
# ChemDataExtractor: Does what we want, doesn't work on PDFs



#sec is a section object, returns a string
def SectiontoPlain(sec):
    retval = ""

    #Put the title in
    retval += "\n\nNEW SECTION: " + sec.title + \
        " (Level: " + str(sec.type) + ")\n"

    #put the paragraphs in
    for i in range(len(sec.para)):
        p = sec.para[i]
        retval += ParatoPlain(p)

    #put the subsections in
    for i in range(len(sec.subsections)):
        retval += SectiontoPlain(sec.subsections[i])
    return retval


#p is a paragraph object, returns a string
def ParatoPlain(p):
    #put paragraph info in
    retval = "\n\nNEW PARA: (Start: pg " + \
        str(p.startPage) + ", col " + str(p.startCol+1)
    retval += "; End: pg " + str(p.endPage) + \
        ", col " + str(p.endCol+1) + ")"
    
    #put the sentences in
    for j in range(len(p.sentences)):
        s = p.sentences[j]
        retval += SenttoPlain(s)
    return retval
        

#s is a sentence object, returns a string.
def SenttoPlain(s):
    retval = "\n\tNEW SENTENCE: (Start: pg " + \
        str(s.startPage) + ", col " + str(s.startCol+1)
    retval += "; End: pg " + \
        str(s.endPage) + ", col " + str(s.endCol+1) + ")" + s.text
    return retval


#takes a PDFdocument object, returns a string.
def PDFtoPlain(PDF, times=[]):
    retval = ""

    if(times):
        retval += TimestoPlain(times)

    for sec in range(len(PDF.sections)):
        retval += SectiontoPlain(PDF.sections[sec])

    retval += "\n\n\n"
    for fig in range(len(PDF.figures)):
        retval += FiguretoPlain(PDF.figures[fig])

    for tab in range(len(PDF.tables)):
        retval += "\n\n\n"
        retval += TabletoPlain(PDF.tables[tab])

    return retval


def TimestoPlain(times):
    retval = "\nAll Times:"

    #Add all the times
    for t in range(len(times)):
        retval += "\nPage " + str(t+1) + ": " + str(times[t])

    #Add the average and median.
    times = minorfunctions.bubbleSort(times)
    retval += "\n\n\nMedian Time per page = " + \
        str(times[int(len(times)/2)])
    retval += "\nAvg Time per page = " + str(sum(times)/len(times))

    return retval


#takes a figure object, returns a string
def FiguretoPlain(figure):
    retval = "\n\n"
    retval += figure.text

    return retval



# takes a tuple of [2d Array of the table, page number]
# returns a string.
def TabletoPlain(Table):

    retval = "NEW TABLE: Page " + str(Table[1])

    Table = Table[0]
    for row in range(len(Table)):
        retval += "\n--------------------------\n"
        for cell in range(len(Table[row])):
            retval += "|"
            for word in range(len(Table[row][cell])):
                if(len(Table[row][cell][word]["text"]) != 0):
                    retval += Table[row][cell][word]["text"]
                    retval += " "

    return retval
