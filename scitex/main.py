import grobidAltoStuff.scitex as scitex
import os

INPUT = "scitexIn"
OUTPUT = "scitexOut"


#run grobid
grobidCMD = "java -Xmx4G -jar ../../grobid/grobid-core/build/libs/grobid-core-0.7.2-onejar.jar -gH ../../grobid/grobid-home -dIn " + INPUT + " -dOut " + OUTPUT + " -exe processFullText -ignoreAssets"

os.system(grobidCMD)

#run pdfalto

for root, dirs, files in os.walk(INPUT):
    for file in files:
        if file.endswith(".pdf"):
            gro = OUTPUT + file[:-4] + ".tei.xml"
            alto = OUTPUT + file[:-4] + "Alto.xml"
            sci = OUTPUT + file[:-4] + "SciTEx.xml"
            
            #run pdfalto
            pdfAltocmd = "grobid-home/pdfalto/lin-64/pdfalto -fullFontName -noLineNumbers -noImage " + file + " " + alto 
            os.system(pdfAltocmd)


            #run scitex
            scitex.addScript(gro, alto, sci)

            #remove grobid and pdfalto outputs
            os.system("rm " + gro)
            os.system("rm " + alto)


