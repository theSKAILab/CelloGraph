# CelloGraph (currently under development)
An ontology and associated tools for cellulose and cellulosic materials

The project contains two separate but interlinked ontologies: 
* The __Cellograph Ontology__ who focuses on terms referring to cellulosic materials, their properties, products, etc. This ontologies is an extension of BFO and reuses some concepts from ChEBI. 
* The __Scientific Publication Ontology (SciPub Ontology)__ which focuses on modeling the metadata and content of a scientific publication. It is intended to be capture the information from a publication in RDF format, focusing on adding information on the contained terms  

## Cellograph Ontology 

The Cellograph Ontology will consist of a core that serves as a _domain reference ontology_ for the domain of cellulose materials. The core refines top-level concepts from BFO to more specific classes, re-using ChEBI concepts as much as possible. 

The upper-most classes are:
* MaterialEntity from BFO (bfo:BFO_0000040)
  + ChemicalEntity from ChEBI (chebi:CHEBI_24431)
    + Substance (cg:CG_0000001) as a generalization of ChEBI's substance to also include other kinds of material substances
      + ChemicalSubstance from ChEBI (chebi:CHEBI_59999)
      + Material (cg:CG_0000002) as a substance in the material science, rather than the chemical sense (though nothing precludes an entity to be both a ChemicalSUbstance and a Material)
        + Cellulosic Material (cg:CG_0000003)
          + Cellulose (cg:CG_0000004)


## SciPub Ontology
