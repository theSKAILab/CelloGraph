BEFORE YOU RUN ANYTHING:

Run these commands so that you have all the stuff u need.

PDF Plumber: 

pip install pdfplumber

Spacy:

pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm



HOW TO USE PDFSort()

PDFSort takes 1 input and that 1 input is a filename. It should be a string of (ideally) the full path to the file in question.

The output is a PDFdocument class object (defined in PDFfragments.py)
	- it has 3 fields: sections, figures, and tables.

	- sections has the following fields:
		self.title : a string of the text present in that header.
        	self.subsections : an array of section objects
       	self.parent : a pointer that is None if this is not a subsection, otherwise it points to the next level up. (i.e. point to section 2. if this is 2.3)
	      self.para : an array of paragraph objects
        	self.type : an integer of what "level" of subheader it is. Level 1 would be "Section 2:" Level 2 would be "2.3", 3 is "1.2.4" etc
        	self.coords : an array of integers describing where this subheader is. Should be empty for headers. 2.3 would have [1] because indices, 1.2.4 would have [0, 1]
        	self.height : Decimal.decimal object. how tall the text is.
        	self.pagenum : integer. what page is it on
        	self.colnum : integer. what column is it in. 

	- paragraph 
		def __init__(self, coords, paraNum, sent=[], cites=[], align=0, start=[0, 0], end=[0, 0]):
        	self.sentences : an array of sentence objects that contain the text of this paragraph.
        	self.coords : same as sectino coords
        	self.paraNum : Integers. which paragraph is this within the section
        	self.citations : not actually used.
        	self.align : Decimal.decimal object. determines
        	self.start : 2-element array of Integers, probably redundant.
        	self.end : 2-element array of Integers, probably redundant.
        	self.startPage = start[0], what page does it start on.
        	self.startCol = start[1], what column does it start in.
        	self.endPage = end[0]
        	self.endCol = end[1]


RUNDOWN OF WHICH FILES CONTAIN WHICH THINGS:

PDFparser.py
	- The major functions of scitex, specifically PDFSort(filename) which I anticipate will be the major way that people interact with it.
	- Other functions are also there for a basic look at how it does stuff.

PDFfragments.py
	- LOOK HERE IF YOU WANNA KNOW WHAT THE OUTPUT IS LIKE
	- Contains all major classes for scitex, including PDFdocument, section, paragraph, and sentence.


PDFfunctions.py
	- The more in-depth details of how it does stuff.
	- There are lots of fundamental functions here like "addLine" "addPara" etc.


PDFsettings.py
	- This has the pdfSettings class which really just hangs onto a lot of variables for me and lets me pass in one variable to functions instead of like 12.
	- most important are probably linespace, lineratio, lineheight, cuz they get used in all lineSettings stuff.

textSettings.py
	- These are the functions that determine whether any individual line is a section header, a figure caption, or just body text.

minorfunctions.py
	- This has a bunch of well, "minor" functions that probably exist in a library somewhere I just didn't bother to go find it.
	- Stuff like "mostCommon" or "isEqualTo"
	- Yes == is a thing that exists but == doesn't let you use an error value now does it?

plaintextwriter.py
	- has functions that turn a PDFdocument class object into a really long string.
