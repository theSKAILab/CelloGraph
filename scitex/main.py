import pdfplumber
from pdfplumber.utils import extract_text
import PDFparser
import PDFfragments
import plaintextwriter
import time
import os

 ###tell it to run for every pdf in a folder instead of an individual document
FILEPATH = "scitex/evalPDF/acsomega.9b01564.pdf"

plumber = pdfplumber.open(FILEPATH)

sec1 = time.time()
output, times = PDFparser.PDFSort(plumber, True)
print("this is just here so I can put a breakpoint here.")
plaintext = plaintextwriter.PDFtoPlain(output, times)
sec2 = time.time()
diff = sec2-sec1
print("Time to Read: " + str(diff) + " sec, aka " + str(diff/60) + " min")
plaintext = "Time to Read: " + \
    str(diff) + " sec, aka " + str(diff/60) + " min" + plaintext
#file = open(("7-18-" + FILEPATH + ".txt"), 'w+', encoding="utf-8")
file = open(("7-19-Gupta.txt"), 'w+', encoding="utf-8")
file.write(plaintext)
file.close()


#FOLDER = "scitex/evalPDF"
#
#for filename in os.listdir(FOLDER):
#    if filename.endswith('.pdf'):
#        plumber = pdfplumber.open(os.path.join(FOLDER, filename))
#
#        
#        sec1 = time.time()
#        output, times = PDFparser.PDFSort(plumber, True)
#
#
#        plaintext = plaintextwriter.PDFtoPlain(output, times)
#        sec2 = time.time()
#        diff = sec2-sec1
#        print("Time to Read: " + str(diff) + " sec, aka " + str(diff/60) + " min")
#
#        plaintext = "Time to Read: " + \
#            str(diff) + " sec, aka " + str(diff/60) + " min" + plaintext
#
#        file = open("7-19-" + filename + ".txt",
#                    'w+', encoding="utf-8")
#        file.write(plaintext)
#        file.close()



#FILEPATH = "scitex/pdfs/Klemm et al.pdf"
#
#plumber = pdfplumber.open(FILEPATH)

# Heinze
# Klemm



#words = something.wordSort(output)

# RDFwriter.dothething(output)
