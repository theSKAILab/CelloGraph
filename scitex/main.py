import pdfplumber
from pdfplumber.utils import extract_text
import PDFparser
import PDFfragments
import plaintextwriter

FILEPATH = "scitex/Heinze.pdf"


plumber = pdfplumber.open(FILEPATH)

# Heinze
# Klemm


output = PDFparser.PDFSort(plumber)

print("this is just here so I can put a breakpoint here.")

plaintext = plaintextwriter.PDFtoPlain(output)

file = open("6_17_Heinze.txt",
            'w+', encoding="utf-8")
file.write(plaintext)
file.close()


#words = something.wordSort(output)

# RDFwriter.dothething(output)
