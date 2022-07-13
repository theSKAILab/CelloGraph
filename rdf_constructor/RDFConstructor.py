from MetadataParser import MetadataParser

class RDFConstructor:

    def namespace(self, uri_name: str, uri: str) -> None:
        triple = "@prefix {} <{}> ."
        
        print(triple.format(uri_name, uri))

    def publication_type(self, pub_name: str) -> None:
        triple_type = ":{} rdf:type sp:ScientificPublication ."
        
        print(triple_type.format(pub_name))

    def publication_info(self, art_desc: dict) -> None:
        triple_title = ":{} sp:title '{}'^^xsd:string ."
        triple_journal_name = ":{} sp:journalName '{}'^^xsd:string ."
        triple_pub_year = ":{} sp:publicationYear '{}'^^xsd:nonNegativeInteger ."
        triple_doi = ":{} sp:doi '{}'^^xsd:string ."
        triple_author = ":{} sp:hasAuthor :Author{} ."
        
        print(triple_title.format(art_desc["pub_name"], art_desc["title"]))
        print(triple_journal_name.format(art_desc["pub_name"], art_desc["journal_name"]))
        print(triple_pub_year.format(art_desc["pub_name"], art_desc["year"]))
        print(triple_doi.format(art_desc["pub_name"], art_desc["doi"]))
        
        for i in range(1, art_desc["no_of_author"] + 1):
            print(triple_author.format(art_desc["pub_name"], i))

    def author(self, no_of_author: int) -> None:
        triple_type = ":Author{} rdf:type sp:PublicationAuthor ."
        triple_position = ":Author{} sp:position '{}'^^xsd:nonNegativeInteger ."
        triple_person = ":Author{} sp:person :Person{} ."
        
        for i in range(1, no_of_author + 1):
            print(triple_type.format(i))
            print(triple_position.format(i, i))
            print(triple_person.format(i, i))

    def person(self, author: list) -> None:
        triple_type = ":Person{} rdf:type sp:Person ."
        triple_first_name = ":Person{} sp:firstName '{}'^^xsd:string ."
        triple_last_name = ":Person{} sp:lastName '{}'^^xsd:string ."
        
        for i in author:
            print(triple_type.format(author.index(i) + 1))
            print(triple_first_name.format(author.index(i) + 1, i.split(",")[1].strip()))
            print(triple_last_name.format(author.index(i) + 1, i.split(",")[0].strip()))

    def organization(self) -> None:
        pass
    
    def text_fragment(self) -> None:
        pass

    def document_part(self, pub_name: str, doc_part: list) -> None:
        triple = ":{} sp:containsDocumentPart :{} ."
        
        for i in doc_part:
            print(triple.format(pub_name, i))

    def section(self, sec_desc: dict) -> None:
        triple_type = ":{} rdf:type sp:Section ."
        triple_num = ":{} sp:secNumber '{}'^^xsd:nonNegativeInteger ."
        triple_frag = ":{} sp:containsFragment :{} ."
        triple_heading = ":{} rdf:type sp:Heading ."
        triple_text = ":{} sp:text '{}'^^xsd:string ."
        triple_para = ":{} rdf:type sp:Paragraph ."
        triple_page_start = ":{} sp:hasStartingPage '{}'^^xsd:nonNegativeInteger ."
        triple_page_end = ":{} sp:hasEndingPage '{}'^^xsd:nonNegativeInteger ."
        triple_col_start = ":{} sp:hasStartingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_col_end = ":{} sp:hasEndingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_line_start = ":{} sp:hasStartingLine '{}'^^xsd:nonNegativeInteger ."
        triple_line_end = ":{} sp:hasEndingLine '{}'^^xsd:nonNegativeInteger ."   
        
        print(triple_type.format(sec_desc["sec_name"]))
        print(triple_num.format(sec_desc["sec_name"], sec_desc["sec_num"]))       
        
        for i in sec_desc["frag"]:
            print(triple_frag.format(sec_desc["sec_name"], i))
            if "Header" in i:
                print(triple_heading.format(i))
                print(triple_text.format(i, sec_desc["sec_text"]))
            else:
                print(triple_para.format(i))
        
        print(triple_page_start.format(sec_desc["sec_name"], sec_desc["page_start"]))
        print(triple_page_end.format(sec_desc["sec_name"], sec_desc["page_end"]))
        print(triple_col_start.format(sec_desc["sec_name"], sec_desc["col_start"]))
        print(triple_col_end.format(sec_desc["sec_name"], sec_desc["col_end"]))
        print(triple_line_start.format(sec_desc["sec_name"], sec_desc["line_start"]))
        print(triple_line_end.format(sec_desc["sec_name"], sec_desc["line_end"]))

    def paragraph(self, para_desc: dict) -> None:
        triple_type = ":{} rdf:type sp:Paragraph ."
        triple_contain_frag = ":{} sp:containsFragment :{} ."
        triple_num = ":{} sp:paraNumber '{}'^^xsd:nonNegativeInteger ."
        triple_page_start = ":{} sp:hasStartingPage '{}'^^xsd:nonNegativeInteger ."
        triple_page_end = ":{} sp:hasEndingPage '{}'^^xsd:nonNegativeInteger ."
        triple_col_start = ":{} sp:hasStartingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_col_end = ":{} sp:hasEndingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_line_start = ":{} sp:hasStartingLine '{}'^^xsd:nonNegativeInteger ."
        triple_line_end = ":{} sp:hasEndingLine '{}'^^xsd:nonNegativeInteger ."
        
        print(triple_type.format(para_desc["para_name"]))
        
        for i in para_desc["contain_frag"]:
            print(triple_contain_frag.format(para_desc["para_name"], i))
        
        print(triple_num.format(para_desc["para_name"], para_desc["para_num"]))
        print(triple_page_start.format(para_desc["para_name"], para_desc["page_start"]))
        print(triple_page_end.format(para_desc["para_name"], para_desc["page_end"]))
        print(triple_col_start.format(para_desc["para_name"], para_desc["col_start"]))
        print(triple_col_end.format(para_desc["para_name"], para_desc["col_end"]))
        print(triple_line_start.format(para_desc["para_name"], para_desc["line_start"]))
        print(triple_line_end.format(para_desc["para_name"], para_desc["line_end"]))

    def sentence(self, sen_desc: dict) -> None:
        triple_type = ":{} rdf:type sp:Sentence ."
        triple_sen_text = ":{} sp:text '{}'^^xsd:string ."
        triple_page_start = ":{} sp:hasStartingPage '{}'^^xsd:nonNegativeInteger ."
        triple_page_end = ":{} sp:hasEndingPage '{}'^^xsd:nonNegativeInteger ."
        triple_col_start = ":{} sp:hasStartingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_col_end = ":{} sp:hasEndingColumn '{}'^^xsd:nonNegativeInteger ."
        triple_line_start = ":{} sp:hasStartingLine '{}'^^xsd:nonNegativeInteger ."
        triple_line_end = ":{} sp:hasEndingLine '{}'^^xsd:nonNegativeInteger ."
        
        print(triple_type.format(sen_desc["sen_name"]))
        print(triple_sen_text.format(sen_desc["sen_name"], sen_desc["sen_text"]))
        print(triple_page_start.format(sen_desc["sen_name"], sen_desc["page_start"]))
        print(triple_page_end.format(sen_desc["sen_name"], sen_desc["page_end"]))
        print(triple_col_start.format(sen_desc["sen_name"], sen_desc["col_start"]))
        print(triple_col_end.format(sen_desc["sen_name"], sen_desc["col_end"]))
        print(triple_line_start.format(sen_desc["sen_name"], sen_desc["line_start"]))
        print(triple_line_end.format(sen_desc["sen_name"], sen_desc["line_end"]))

    def figure(self, fig_desc: dict) -> None:
        triple_type = ":{} rdf:type sp:Figure ."
        triple_num = ":{} sp:figureNumber '{}'^^xsd:nonNegativeInteger ."
        triple_text = ":{} sp:text '{}'^^xsd:^^xsd:string ."
        triple_page_num = ":{} sp:page '{}'^^xsd:nonNegativeInteger ."
        
        print(triple_type.format(fig_desc["fig_name"]))
        print(triple_num.format(fig_desc["fig_name"], fig_desc["fig_num"]))
        print(triple_text.format(fig_desc["fig_name"], fig_desc["fig_text"]))
        print(triple_page_num.format(fig_desc["fig_name"], fig_desc["page_num"]))

    def table(self, tab_desc: dict) -> None:
        triple_type = ":{} rdf:type sp:Table ."
        triple_num = ":{} sp:tableNumber '{}'^^xsd:nonNegativeInteger ."
        triple_text = ":{} sp:text '{}'^^xsd:^^xsd:string ."
        triple_page_num = ":{} sp:page '{}'^^xsd:nonNegativeInteger ."      
        
        print(triple_type.format(tab_desc["tab_name"]))
        print(triple_num.format(tab_desc["tab_name"], tab_desc["tab_num"]))
        print(triple_text.format(tab_desc["tab_name"], tab_desc["tab_text"]))
        print(triple_page_num.format(tab_desc["tab_name"], tab_desc["page_num"]))

    def term(self, pub_name: str, term_desc: dict) -> None:
        triple_contain_term = ":{} sp:containsTerm :{} ."
        triple_type = ":{} rdf:type sp:Term ."
        triple_race = ":{} sp:race sp:{} ."
        triple_text = ":{} sp:text '{}'^^xsd:string ."
        triple_status = ":{} :hasStatus :{} ."
        triple_loc = ":{} sp:occursInText :{} ."
        
        print(triple_contain_term.format(pub_name, term_desc["term_name"]))
        print(triple_type.format(term_desc["term_name"]))
        print(triple_race.format(term_desc["term_name"], term_desc["term_race"]))
        print(triple_text.format(term_desc["term_name"], term_desc["term_text"]))
        print(triple_status.format(term_desc["term_name"], term_desc["term_status"]))
        
        for i in term_desc["term_in"]:
            print(triple_loc.format(term_desc["term_name"], i))

    def term_status(self) -> None:
        pass

    def bibliography(self, bib_desc: dict):
        triple_type = ":{} rdf:type sp:BibliographicEntry ."
        triple_ref_num = ":{} sp:refNumber '{}'^^xsd:nonNegativeInteger ."
        triple_text = ":{} sp:text '{}'^^xsd:string ."
        
        print(triple_type.format(bib_desc["bib_name"]))
        print(triple_ref_num.format(bib_desc["bib_name"], bib_desc["bib_ref_num"]))
        print(triple_text.format(bib_desc["bib_name"], bib_desc["bib_text"]))

if __name__ == "__main__":
    rdf_constructor = RDFConstructor()

    metadata_parser = MetadataParser()
    metadata_parser.read_ris_file("ris_metadata.ris")
    
    print("-------------------- NAMESPACE --------------------")
    rdf_constructor.namespace(uri_name = ":", uri = "http://cellograph.com/SciPub/2022v1.0/")
    rdf_constructor.namespace(uri_name = "sp:", uri = "http://cellograph.com/SciPub/2022v1.0/")
    rdf_constructor.namespace(uri_name = "rdf:", uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdf_constructor.namespace(uri_name = "rdfs:", uri = "http://www.w3.org/2000/01/rdf-schema#")
    rdf_constructor.namespace(uri_name = "xsd:", uri = "http://www.w3.org/2001/XMLSchema#")
    rdf_constructor.namespace(uri_name = "owl:", uri = "http://www.w3.org/2002/07/owl#")

    print("-------------------- PUBLICATION_TYPE --------------------")
    rdf_constructor.publication_type(pub_name = "pubA")
    
    print("-------------------- PUBLICATION_INFO --------------------")
    rdf_constructor.publication_info(art_desc = {
        "pub_name": "pubA", 
        "title": metadata_parser.primary_title(),
        "journal_name": metadata_parser.journal_name(),
        "year": metadata_parser.year(),
        "doi": metadata_parser.doi(),
        "no_of_author": metadata_parser.no_of_authors()
        })

    print("-------------------- PUBLICATION_AUTHOR --------------------")
    rdf_constructor.author(no_of_author = metadata_parser.no_of_authors())

    print("-------------------- PERSON --------------------")
    rdf_constructor.person(author = metadata_parser.authors())
    
    print("-------------------- DOCUMENT_PART --------------------")
    rdf_constructor.document_part(
        pub_name = "pubA", 
        doc_part = ["Figure1", "Figure2", "Figure3", "Table1", "Keyword1", "BibliographicEntry1", "BibliographicEntry2"]
        )
    
    print("-------------------- SECTION --------------------")
    rdf_constructor.section(sec_desc = {
        "sec_name": "pubASec2", 
        "sec_num": 2, 
        "sec_text": "Nanocellulose", 
        "frag": ["pubASec2Header", "Paragraph3", "Paragraph4", "Paragraph5"], 
        "page_start": 2, 
        "page_end": 2, 
        "col_start": 1, 
        "col_end": 2, 
        "line_start": 11, 
        "line_end": 34
        })
    
    print("-------------------- PARAGRAPH --------------------")
    rdf_constructor.paragraph(para_desc = {
        "para_name": "Paragraph1", 
        "contain_frag": ["Para1Sent1", "Para1Sent2", "Para1Sent3"], 
        "para_num": 1, 
        "page_start": 1, 
        "page_end": 1, 
        "col_start": 1, 
        "col_end": 2, 
        "line_start": 3, 
        "line_end": 9
        })
    
    print("-------------------- SENTENCE --------------------")
    rdf_constructor.sentence(sen_desc = {
        "sen_name": "Para1Sent2", 
        "sen_text": "Nanocellulose is a natural nanomaterial which can be extracted from plant cell wall.", 
        "page_start": 1, 
        "page_end": 1, 
        "col_start": 2, 
        "col_end": 2, 
        "line_start": 2, 
        "line_end": 3
        })
    
    print("-------------------- FIGURE --------------------")
    rdf_constructor.figure(fig_desc = {
        "fig_name": "Figure1", 
        "fig_num": 1, 
        "fig_text": "Main structure of plant cell wall in lignocellulosic biomass which is consisted of lignin, hemicellulose, and cellulose.", 
        "page_num": 2
        })
    
    print("-------------------- TABLE --------------------")
    rdf_constructor.table(tab_desc = {
        "tab_name": "Table1", 
        "tab_num": 1, 
        "tab_text": "Progress of nanocellulose extraction by ball milling.", 
        "page_num": 8
        })
    
    print("-------------------- TERM --------------------")
    rdf_constructor.term(pub_name="pubA", term_desc = {"term_name": "Term1", "term_race": "SingleTerm", "term_text": "Cellulose", "term_status": "ConfirmedStatus1", "term_in": ["AbsSent1", "Para1Sent3", "Para2Sent2"]})
    
    print("-------------------- BIBLIOGRAPHY --------------------")
    rdf_constructor.bibliography(bib_desc = {
        "bib_name": "BibliographicEntry1", 
        "bib_ref_num": 1, 
        "bib_text": "A. Dufresne, Nanocellulose: a new ageless bionanomaterial, Mater. Today 16 (2013) 220–227."
        })


