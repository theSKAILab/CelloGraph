import rispy

class MetadataParser:
    
    def read_ris_file(self, filename) -> None:
        file_path = filename
        with open(file_path, "r") as bibliography_file:
            self.entries = rispy.load(bibliography_file)

    def type_of_reference(self) -> str:
        type_of_reference = self.entries[0]["type_of_reference"]
        return type_of_reference

    def primary_title(self) -> str:
        primary_title = self.entries[0]["primary_title"]
        return primary_title

    def no_of_authors(self) -> int:
        no_of_authors = len(self.entries[0]["authors"])
        return no_of_authors

    # def authors(self) -> dict:
    #     author_list = self.entries[0]["authors"].copy()
    #     authors = dict()
    #     for index, author_name in enumerate(author_list, start=1):
    #         authors[index] = author_name
    #     return authors

    def authors(self) -> list:
        authors = self.entries[0]["authors"].copy()
        return authors

    def journal_name(self) -> str:
        journal_name = self.entries[0]["journal_name"]
        return journal_name

    def volume(self) -> str:
        volume = self.entries[0]["volume"]
        return volume

    def number(self) -> str:
        number = self.entries[0]["number"]
        return number

    def start_page(self) -> str:
        start_page = self.entries[0]["start_page"]
        return start_page
    
    def end_page(self) -> str:
        end_page = self.entries[0]["end_page"]
        return end_page

    def year(self) -> str:
        year = self.entries[0]["year"]
        return year

    def date(self) -> str:
        date = self.entries[0]["date"]
        return date
        
    def issn(self) -> str:
        issn = self.entries[0]["issn"]
        return issn

    def doi(self) -> str:
        doi = self.entries[0]["doi"]
        return doi

    def url(self) -> str:
        url = self.entries[0]["url"]
        return url

    def keywords(self) -> list:
        keywords = self.entries[0]["keywords"].copy()
        return keywords

    def abstract(self) -> str:
        abstract = self.entries[0]["abstract"]
        return abstract

# metadata_parser = MetadataParser()
# metadata_parser.read_ris_file("ris_metadata.ris")
# print(metadata_parser.abstract())
# print(metadata_parser.entries)
