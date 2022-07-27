import pdfplumber
from pdfplumber.utils import extract_text
import PDFparser
import PDFfragments
import PDFsettings
import PDFfunctions
import plaintextwriter


table_settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text"
}

FILEPATH = "scitex/evalPDF/acsomega.9b01564.pdf"

plumber = pdfplumber.open(FILEPATH)

VERTICAL_ERROR = 5
HORIZONTAL_ERROR = 30
RATIO_MARGIN = 0.05
PARAS_REQUIRED = 2

PDF = PDFfragments.PDFdocument()
pdfSettings = PDFsettings.PDFsettings(
    plumber, VERTICAL_ERROR, HORIZONTAL_ERROR, PARAS_REQUIRED)

pdfSettings.activesection = PDFfragments.section(
    "5", None, [0], 1, 11, 18)

PDF.sections.append(pdfSettings.activesection)
PDF, pdfSettings = PDFparser.DealWithPage(PDF, plumber.pages[2], pdfSettings)

page = plumber.pages[2]
words = PDFfunctions.getWords(page, HORIZONTAL_ERROR)
visible = words[300:]
hate = words[600:]

tables = page.extract_tables(table_settings)

words = PDFfunctions.removePageHeadersEarly(
    words, page.page_number, pdfSettings)



#PDF, words = PDFfunctions.removeTables(
#    PDF, pdfSettings, page, words)

words, lines, pdfSettings = PDFfunctions.getLines(
    words, pdfSettings, pdfSettings.intraline)





#PDF, words, lines, lineIndex, pdfSettings, pagenum
i = -1
while i < len(lines)-1:
    i += 1
    PDF, pdfSettings, lines, i = PDFparser.DealWithLine(
        PDF, words, lines, i, pdfSettings, page.page_number, 0)


plaintext = plaintextwriter.PDFtoPlain(PDF)

file = open("evalTestOutput.txt",
            'w+', encoding="utf-8")
file.write(plaintext)
file.close()
