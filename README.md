# CelloGraph (currently under development)
An ontology and associated tools for cellulose and cellulosic materials

The project contains two separate but interlinked ontologies: 
* The __Cellograph Ontology__ who focuses on terms referring to cellulosic materials, their properties, products, etc. This ontologies is an extension of BFO and reuses some concepts from ChEBI. 
* The __Ontology for Named Entity Representation (OnNER)__ which focuses on modeling named entities as they appear in scientific publications and what is necessary to locate them therein. It is intended to be used to capture each publication and all its named entities as an RDF document  

## Cellograph Ontology 

The Cellograph Ontology will consist of a core that serves as a _domain reference ontology_ for the domain of cellulose materials. The core refines top-level concepts from BFO to more specific classes, re-using ChEBI concepts as much as possible. 

The upper-most classes are:
* MaterialEntity from BFO (bfo:BFO_0000040)
  + ChemicalEntity from ChEBI (chebi:CHEBI_24431)
    + Substance (cg:CG_0000001) as a generalization of ChEBI's substance to also include other kinds of material substances
      + ChemicalSubstance from ChEBI (chebi:CHEBI_59999)
      + Material (cg:CG_0000002) as a substance in the material science, rather than the chemical sense (though nothing precludes an entity to be both a ChemicalSubstance and a Material)
        + Organic Material (cg:CG_0000003)
          + Cellulosic Material (cg:CG_0000005)
            + Cellulose (cg:CG_0000010)
        + Inorganic Material (cg:CG_0000004)
          + Metallic Material (cg:CG_0000006)
          + Ceramic Material (cg:CG_0000007)
        + Polymeric Material (cg:CG_0000008)
        + Textile Material (cg:CG_0000009)


## OnNER
