1. Retrieve training data. Logic: Retrieve only those entities whose latest status is neither Rejected nor Candidate.
	
	```
    SELECT ?paragraph ?entity ?offset ?length ?label ?status
    WHERE {
        ?entId rdf:type onner:LabeledTerm ;
               onner:labeledTermText ?entity ;
               onner:offset ?offset ;
               onner:length ?length ;
               onner:labeledTermDirectlyContainedBy ?paraId ;
               onner:hasLabeledTermStatus ?status .

        ?paraId onner:paragraphText ?paragraph .

        ?status onner:statusAssignmentDate ?datetime ;
                onner:hasLabeledTermLabel ?labelId .

        ?labelId onner:labelText ?label .

        FILTER NOT EXISTS {
            ?entId onner:hasLabeledTermStatus ?newerStatus .
            ?newerStatus onner:statusAssignmentDate ?newerDatetime .

            FILTER(?newerDatetime > ?datetime)
        }

        FILTER(
            !STRSTARTS(STR(?status), STR(data:Rejected_)) &&
            !STRSTARTS(STR(?status), STR(data:Candidate_))
        )
    }
    ORDER BY ?paraId ?offset
	```
	

2. Retrieve candidate data. Logic: Retrieve all terms from paragraphs containing at least one candidate term that has not yet been reviewed.

    ```
    PREFIX onner: <http://purl.org/spatialai/onner/onner-full#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?paraId ?paragraph ?entId ?entity ?offset ?length ?label ?status ?annotator ?datetime
    WHERE {
        ?paraId onner:directlyContainsLabeledTerm ?entId .
        
        ?entId rdf:type onner:LabeledTerm ;
            onner:labeledTermText ?entity ;
            onner:offset ?offset ;
            onner:length ?length ;
            onner:hasLabeledTermStatus ?status .
        
        ?status onner:statusAssignmentDate ?datetime ;
        		onner:statusAssignedBy ?annotator ;
        		onner:hasLabeledTermLabel ?labelId .
        
        ?labelId rdf:type onner:Label ;
        		 onner:labelText ?label .
        
        ?paraId rdf:type onner:Paragraph ;
        		onner:paragraphText ?paragraph .
        
        {
            SELECT DISTINCT ?paraId
            WHERE {
                ?entId2 rdf:type onner:LabeledTerm ;
                	   onner:labeledTermDirectlyContainedBy ?paraId ;
                       onner:hasLabeledTermStatus ?status .
                ?status rdf:type onner:CandidateStatus .   
    
                {
                    SELECT ?entId2 (COUNT(?allStatus) AS ?statusCount)
                    WHERE {
                        ?entId2 onner:hasLabeledTermStatus ?allStatus .
                    }
                    GROUP BY ?entId2
                    HAVING (?statusCount = 1)
                }
            }
        }
    }
    ORDER BY ?paraId ?offset
    ```
    
    
3. Retrieve candidate data. Logic: Retrieve only the candidate terms from paragraphs that have not yet been reviewed.

    ```
    PREFIX onner: <http://purl.org/spatialai/onner/onner-full#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?paraId ?paragraph ?entId ?entity ?offset ?length ?label ?status ?annotator ?datetime
    WHERE {
        ?entId rdf:type onner:LabeledTerm ;
            onner:labeledTermText ?entity ;
            onner:offset ?offset ;
            onner:length ?length ;
        	onner:labeledTermDirectlyContainedBy ?paraId ;
            onner:hasLabeledTermStatus ?status .
    
        ?status rdf:type onner:CandidateStatus ;
        		onner:statusAssignmentDate ?datetime ;
        		onner:statusAssignedBy ?annotator ;
        		onner:hasLabeledTermLabel ?labelId .
        
        ?labelId rdf:type onner:Label ;
        		 onner:labelText ?label .
        
        ?paraId rdf:type onner:Paragraph ;
        		onner:paragraphText ?paragraph .
    
        {
            SELECT ?entId (COUNT(?allStatus) AS ?statusCount)
            WHERE {
                ?entId onner:hasLabeledTermStatus ?allStatus .
            }
            GROUP BY ?entId
            HAVING (?statusCount = 1)
        }
    }
    ORDER BY ?paraId ?offset
    ```
    
