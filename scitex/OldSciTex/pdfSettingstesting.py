import pdfSettings
import pdfplumber

FILEPATH = "scitex/Heinze.pdf"

plumber = pdfplumber.open(FILEPATH)

VERTICAL_ERROR = 5
HORIZONTAL_ERROR = 10
RATIO_MARGIN = 0.05
PARAS_REQUIRED = 2

PDF = PDFfragments.PDFdocument()
