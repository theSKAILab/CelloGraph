import PDFfragments
import minorfunctions


#Takes a pdf and returns a really long string.
#Times is used for debug purposes, it's an array of floats describing how long it took to read each page.
def PDFtoPlain(PDF, times=[]):
    retval = ""

    #if we want to print the times, then do that.
    if(times):
        retval += TimestoPlain(times)

    #print all the sections
    for sec in range(len(PDF.sections)):
        retval += SectiontoPlain(PDF.sections[sec])

    #print all the figures.
    retval += "\n\n\n"
    for fig in range(len(PDF.figures)):
        retval += FiguretoPlain(PDF.figures[fig])

    #print all the tables.
    for tab in range(len(PDF.tables)):
        retval += "\n\n\n"
        retval += TabletoPlain(PDF.tables[tab])

    return retval


#prints each time, then prints the average and median times.
def TimestoPlain(times):
    retval = "\nAll Times:"
    for t in range(len(times)):
        retval += "\nPage " + str(t+1) + ": " + str(times[t])
    times = minorfunctions.bubbleSort(times)
    retval += "\n\n\nMedian Time per page = " + \
        str(times[int(len(times)/2)])
    retval += "\nAvg Time per page = " + str(sum(times)/len(times))
    return retval


#takes a section object, returns a string.
def SectiontoPlain(sec):
    retval = ""

    #print the name of the section.
    retval += "\n\nNEW SECTION: " + sec.title + \
        " (Level: " + str(sec.type) + ")\n"

    #print the paragraphs.
    for i in range(len(sec.para)):
        p = sec.para[i]
        retval += ParatoPlain(p)
        
    #print the subsections.
    for i in range(len(sec.subsections)):
        retval += SectiontoPlain(sec.subsections[i])
    return retval


#takes a paragrpah object, returns a string.
def ParatoPlain(para):

    #print information about this paragraph.
    retval = "\n\nNEW PARA: (Start: pg " + \
            str(para.startPage) + ", col " + str(para.startCol+1)
    retval += "; End: pg " + str(para.endPage) + \
            ", col " + str(para.endCol+1) + ")"

    #print each sentence.
    for j in range(len(para.sentences)):
        s = para.sentences[j]
        retval += SenttoPlain(s)

    return retval
            

#takes a sentence object, returns a string.
#prints info about the sentence + the sentence text.
def SenttoPlain(sent):
    retval = "\n\tNEW SENTENCE: (Start: pg " + \
        str(sent.startPage) + ", col " + str(sent.startCol+1)
    retval += "; End: pg " + \
        str(sent.endPage) + ", col " + str(sent.endCol+1) + ")" + sent.text
    return retval




# takes a figure object, returns a string.
# just returns the figure text.
def FiguretoPlain(figure):
    retval = "\n\n"
    retval += figure.text

    return retval


#takes a table object, returns a long string.
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
