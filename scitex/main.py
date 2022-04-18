from pdfminer.pdfdocument import PDFDocument
import pdfplumber
from pdfplumber.utils import extract_text
import PDFparser
import PDFfragments
import plaintextwriter

FILEPATH = "scitex/Gupta et al.pdf"
#FILEPATH = "Heinze.pdf"
#FILEPATH = "Klemm et al.pdf"


plumber = pdfplumber.open(FILEPATH)


# Heinze 30
# Klemm, -


output = PDFparser.PDFSort(plumber)

print("this is just here so I can put a breakpoint here.")

plaintext = plaintextwriter.PDFtoplain(output)

file = open("debug output.txt", 'w')
file.write(plaintext)
file.close()


#words = something.wordSort(output)

# RDFwriter.dothething(output)
