import pdfplumber
from pdfplumber.utils import extract_text
import PDFparser
import PDFfragments
import plaintextwriter
import time

FILEPATH = "scitex/pdfs/Heinze.pdf"


plumber = pdfplumber.open(FILEPATH)

# Heinze
# Klemm

sec1 = time.time()
output, times = PDFparser.PDFSort(plumber, True)

print("this is just here so I can put a breakpoint here.")


plaintext = plaintextwriter.PDFtoPlain(output, times)
sec2 = time.time()
diff = sec2-sec1
print("Time to Read: " + str(diff) + " sec, aka " + str(diff/60) + " min")

plaintext = "Time to Read: " + \
    str(diff) + " sec, aka " + str(diff/60) + " min" + plaintext

file = open("7-6-Heinze.txt",
            'w+', encoding="utf-8")
file.write(plaintext)
file.close()


#words = something.wordSort(output)

# RDFwriter.dothething(output)
