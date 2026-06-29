1. Retrieving training data from GraphDB. Retrieval logic: include only entities whose latest status is neither Rejected nor Candidate.
	
	```
    SELECT ?paragraph ?entity ?offset ?length ?label ?status
    WHERE {{
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

        FILTER NOT EXISTS {{
            ?entId onner:hasLabeledTermStatus ?newerStatus .
            ?newerStatus onner:statusAssignmentDate ?newerDatetime .

            FILTER(?newerDatetime > ?datetime)
        }}

        FILTER(
            !STRSTARTS(STR(?status), STR(data:Rejected_)) &&
            !STRSTARTS(STR(?status), STR(data:Candidate_))
        )
    }}
    ORDER BY ?paraId ?offset
	```
	


