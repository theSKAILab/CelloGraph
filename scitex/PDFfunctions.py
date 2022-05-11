import spacy
from spacy.matcher import Matcher
import textprocessing
import PDFfragments
import minorfunctions


def getDiffs(words, pdfSettings, ERROR_MARGIN):
    diffs = []
    bookmark = 0
    for w in range(len(words)-1):
        # if the first word is lowercase, then a paragraph probably got split up.
        if(w == 0):
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(words[0]["text"])
            if(doc[0].is_lower):
                pdfSettings.addto = True

        diff = float(words[w+1]["top"] - words[w]["top"])

        if(diff - ERROR_MARGIN > 0):
            aftspace = float(words[w+1]["top"] - words[w]["bottom"])
            befspace = float(words[w]["top"] - words[bookmark]["bottom"])
            if bookmark == 0:
                befspace = aftspace
            height = float(words[w]["bottom"] - words[w]["top"])
            aftRatio = height/aftspace
            befRatio = height/befspace
            diffs.append({"LineEndDex": w, "AftSpace": aftspace,
                         "BefSpace": befspace, "Height": height, "AftRatio": aftRatio, "BefRatio": befRatio,
                          "Align": words[w]["x0"], "Text": words[bookmark+1:w+1]})
            bookmark = w
    return diffs, pdfSettings

# adds the contents of a section header to another section
# tomove is Section header whose contents will be moved.
# destination is a Section header who will receive tomove's contents.
# tomove's contents will be added at the end of destination
# If destination has subsections, tomove's contents will be added there instead.


def moveSection(tomove, destination):
    # check to see if there's a subsection we should be putting this in
    check = 0
    if(len(destination.subsections) > 0):
        check = len(destination.subsections[len(
            destination.subsections)-1].subsections)

    if(check == 0):
        for i in range(len(tomove.subsections)):
            destination.subsections.append(
                copy.deepcopy(tomove.subsections[i]))
        for i in range(len(tomove.para)):
            destination.para.append(copy.deepcopy(tomove.para[i]))
    else:
        moveSection(
            tomove, destination.subsections[len(destination.subsections)-1])


def addSection(header, title, type, PDF, recursionlevel=0):
    # if it's broken return false
    if(type == 0 or header == None or recursionlevel > 9):
        PDF.sections.append(PDFfragments.section(
            "ERROR:SECTION_MISSING" + title, header.parent))

    # if it's a section header, add it to the PDF's list
    elif(type == 1):
        PDF.sections.append(PDFfragments.section(title, header.parent))

    # if it's the current header's sibling, add it to the parent's list
    elif(type == header.type):
        header.parent.subsections.append(
            PDFfragments.section(title, header.parent))

    # if it's a child of the current header, add it to the current header's list
    elif(type == header.type + 1):
        header.subsections.append(PDFfragments.section(title, header))

    # if it's an uncle of the current header, recurse upwards.
    elif(type < header.type):
        if(header.parent and header.parent.parent):
            addSection(header.parent, title, type, PDF, recursionlevel+1)
        else:
            PDF.sections.append(PDFfragments.section(title, header.parent))

    # if it's a grandchild of the current header, recurse downwards.
    elif(type > header.type):
        next = header.lastsub()[0]
        if(next):
            addSection(next, title, type, PDF, recursionlevel+1)
        else:
            header.subsections.append(
                PDFfragments.section("ERROR:SECTION_MISSING" + title, header))


# Intent is to remove running headers at the top of the page that get marked as headers
# This is achieved by removing sections with duplicate headers.


def removePageHeaders(PDF):
    single = []
    remove = []
    # for each section header, if there's an identical section header, flag both to be removed.
    # each element of remove is (index, sectiontitle)
    for h in range(len(PDF.sections)):
        title = PDF.sections[h].title
        titleinsingle = False

        # check if we've seen this title already
        for i in range(len(single)):
            if(single[i][1] == title):
                titleinsingle = True

        # if we haven't, add it to the list of things we've seen.
        if(not titleinsingle):
            single.append((h, PDF.sections[h].title))

        # if we have, add it to the list of things to remove
        else:
            if h not in remove:
                for j in range(len(single)):
                    if single[j][1] == title and single[j] not in remove:
                        remove.append(single[j])
            remove.append((h, PDF.sections[h].title))

    # now go through and remove them all. Any text under that header will be put under the previous header.
    for i in range(len(remove)-1, -1, -1):
        if(remove[i][0] != 0 and remove[i][0] < len(PDF.sections)-1):
            minorfunctions.moveSection(PDF.sections[remove[i][0]],
                                       PDF.sections[remove[i][0]-1])
            PDF.sections.pop(remove[i][0])


# removes any headers that are actually just figure or table descriptions.
# figures and graphics get added to PDF.figures
# tables get added to PDF.tables

def removeFigureHeaders(PDF):
    # set up some spacy stuff
    nlp = spacy.load("en_core_web_sm")
    figurematcher = Matcher(nlp.vocab)
    figurepattern = [{"LOWER": "figure"}, {"IS_DIGIT": True}]
    figpattern = [{"LOWER": "fig"}, {"IS_PUNC": True}, {"IS_DIGIT": True}]
    tablepattern = [{"LOWER": "table"}, {"IS_DIGIT": True}]
    tabpattern = [{"LOWER": "tab"}, {"IS_PUNC": True}, {"IS_DIGIT": True}]
    graphicpattern = [{"LOWER": "graphic"}, {"IS_DIGIT": True}]
    graphpattern = [{"LOWER": "graph"}, {"IS_DIGIT": True}]

    figurematcher.add(
        "figures", [figurepattern, figpattern, tablepattern, tabpattern, graphicpattern, graphpattern])

    for i in range(len(PDF.sections)-1, 0, -1):
        doc = nlp(PDF.sections[i].title)
        matches = figurematcher(doc)

        if len(matches) > 0:
            minorfunctions.moveSection(PDF.sections[i], PDF.sections[i-1])
            sectioncopy = PDF.sections[i].copy()
            sectioncopy.parent = PDF.sections[i-1]
            PDF.sections[i-1].subsections.append(sectioncopy)
            PDF.figures.append(sectioncopy.title)
            PDF.sections.pop(i)
