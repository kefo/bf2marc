profile = [
    {
        "note": "This is looking at the work; it should be taking from admin metadata on the instance.",
        "query": """
            SELECT DISTINCT ?field ?data
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:adminMetadata/bf:source/rdfs:label ?data .
                BIND( "003" as ?field ) .
            }
            LIMIT 1
        """,
    },
    {
        "note": "This is looking at the work; it should be taking from admin metadata on the instance. Also, ideally there would be multiple adminmetadatas, must choose oldest one.",
        "query": """
            SELECT DISTINCT ?field ?data
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:adminMetadata/bf:changeDate ?cd .
                BIND(CONCAT(STR(YEAR(?cd)), STR(MONTH(?cd)), STR(DAY(?cd)), STR(HOURS(?cd)), STR(MINUTES(?cd)), STR(SECONDS(?cd)), ".0") as ?data) .
                BIND( "005" as ?field ) .
            }
            LIMIT 1
        """,
    },
    # 006
    # 007
    # 008
    {
        "query": """
            SELECT DISTINCT ?field ?a 
            WHERE {
                ?instance bf:identifiedBy ?id .
                ?id a bf:Lccn .
                ?id rdf:value ?a .
                BIND( "010" as ?field ) .
            }
            LIMIT 1
        """,
    },
    # 013
    # 015
    # 016
    # 017
    # 018
    {
        "note": "Handle qualifer? and cancelled?",
        "query": """
            SELECT DISTINCT ?field ?a 
            WHERE {
                ?instance bf:identifiedBy ?id .
                ?id a bf:Isbn .
                ?id rdf:value ?a .
                BIND( "020" as ?field ) .
            }
            LIMIT 1
        """,
    },
    # 022
    # 024
    # 026
    # 027
    # 028
    # 030
    # 031
    # 032
    # 033 - this is for an event - what is the mapping for this even?
    # 034
    # 035 - things like OCLCnum and others....
    # 037
    # 038
    {
        "note": "It is impossible to determine $a or $d from the BF.  If this information is important, it is not capture per LC. No language of description either?",
        "query": """
            SELECT DISTINCT ?field ?e
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:adminMetadata/bf:descriptionConventions/rdfs:label ?e .
                BIND( "040" as ?field ) .
            }
            LIMIT 1
        """,
    },
    {
        "note": "This only handles the most basic language.",
        "query": """
            SELECT DISTINCT ?field ?a
            WHERE {
                ?work bf:hasInstance ?instance .
                OPTIONAL {
                    OPTIONAL { ?work bf:language/rdfs:label ?astr . }
                    ?work bf:language ?l .
                    BIND( IF(BOUND(?astr), ?astr, SUBSTR(STR(?l), STRLEN(STR(?l)) - 2)) as ?a ).
                }
                BIND( "041" as ?field ) .
            }
        """,
    },
    {
        "note": "It is impossible to determine $a or $d from the BF.  If this information is important, it is not capture per LC. No language of description either?",
        "query": """
            SELECT DISTINCT ?field ?a
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:adminMetadata/bf:descriptionAuthentication/rdf:value ?a .
                BIND( "042" as ?field ) .
            }
            LIMIT 1
        """,
    },
    # 043
    # 044
    # 045
    # 046
    # 047
    # 048
    {
        "note": "bf:itemPortion is in the class part at the work level.  That's a shame.  In bfdr, figure out a way to do this at the item level.  How is 'at lc' or not at lc handled? Is it just assumed to be at LC?",
        "query": """
            SELECT DISTINCT ?field ?first_ind ?second_ind ?a ?b
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:classification ?class .
                ?class a bf:ClassificationLcc .
                ?class bf:classificationPortion ?a .
                OPTIONAL {
                    ?class bf:itemPortion ?b .
                }
                OPTIONAL {
                    ?class bf:source ?source .
                    BIND(
                        IF (STR(?source) = "http://id.loc.gov/vocabulary/organizations/dlc",
                            "0",
                            "4"
                        )
                    as ?second_ind ).
                }
                BIND( "0" as ?first_ind ) .
                BIND( "050" as ?field ) .
            }
        """,
    },
    # 051
    # 052
    # 055
    # 060
    # 061
    # 066
    # 070
    # 071
    # 072
    # 074
    # 080
    {
        "note": "Guessing with 'abridged.' What happens with $2?  And WTF?  Why are there URIs for edition as strings in the rdf? This is a complete cluster.",
        "query": """
            SELECT DISTINCT ?field ?first_ind ?second_ind ?a ?2
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:classification ?class .
                ?class a bf:ClassificationDdc .
                ?class bf:classificationPortion ?a .
                BIND(
                    IF (EXISTS{?class bf:edition "full"},
                        "0",
                        IF (EXISTS{?class bf:edition "abridged"},
                            "1",
                            IF (EXISTS{?class bf:edition ?class_edition},
                                "7",
                                "#"
                            )
                        )
                    )
                as ?first_ind ) .
                OPTIONAL {
                    ?class bf:assigner ?assigner .
                    BIND(
                        IF (STR(?assigner) = "http://id.loc.gov/vocabulary/organizations/dlc", 
                            "0",
                            "4"
                        )
                    as ?second_ind) .
                }
                OPTIONAL {
                    ?class bf:edition ?edition .
                    FILTER(STR(?edition) != "full" && STR(?edition) != "abridged") .
                    BIND( REPLACE(STR(?edition), "http://id.loc.gov/vocabulary/classSchemes/ddc","", "q") as ?2).
                }
                BIND(
                    IF (!BOUND(?second_ind), 
                        "#",
                        ?second_ind
                    )
                as ?second_ind) .
                BIND( "082" as ?field ) .
            }
        """,
    },
    # 083
    # 084
    # 085
    # 086
    # 088
    
    # Note: the below takes care of 1XX and 7XX, when they are contributors
    {
        "note": "This treats it as an authority, because, well, that's what LC does. first_ind - how is that actually done?",
        "query": """
            SELECT DISTINCT ?field ?first_ind ?0 ?a ?e ?4
            WHERE {
                ?work bf:contribution ?contribution .
                OPTIONAL {
                    ?contribution bf:role/rdfs:label ?e .
                }
                OPTIONAL {
                    ?contribution bf:role ?role .
                    BIND(
                        IF (isIRI(?role), 
                            SUBSTR(STR(?role), STRLEN(STR(?role)) - 2),
                            ""
                        )
                    as ?4 ).
                }
                ?contribution bf:agent ?agent .
                
                BIND( IF(isURI(?agent), STR(?agent), "") as ?0 ) .

                ?agent a ?agent_type .
                VALUES(?agent_type ?fieldtype) { 
                    (bf:Person "00")
                    (bf:Organization "10")
                    (bf:Meeting "11")
                } .
                BIND( IF (EXISTS { ?contribution a bflc:PrimaryContribution . }, CONCAT("1", ?fieldtype), CONCAT("7", ?fieldtype)) as ?field ) .
                
                VALUES(?agent_type ?first_ind) { 
                    (bf:Person "1")
                    (bf:Organization "2")
                    (bf:Meeting "2")
                } .
                
                ?agent rdfs:label ?a .

            }
        """,
    },
    # 130
    # 210
    # 222
    # 240
    # 242
    # 243
    {
        "note": "A lot of fields may be unaccommodated here.  Indicators are going to take some work.",
        "query": """
            SELECT DISTINCT ?field ?a ?c
            WHERE {
                ?work bf:hasInstance ?instance .
                OPTIONAL {
                    ?instance bf:responsibilityStatement ?c .
                }
                ?work bf:title ?t .
                ?t bf:mainTitle ?a .
                BIND( "245" as ?field ) .
            }
            LIMIT 1
        """,
    },
    # 246
    # 247
    # 250
    # 251
    # 254
    # 255
    # 256
    # 257
    # 258
    # 260 - This will never be used.  264 being used instead.
    # 263
    {
        "query": """
            SELECT DISTINCT ?field ?first_ind ?second_ind ?a ?b ?c 
            WHERE {
                ?instance bf:provisionActivity ?pa .
                ?pa a ?pa_type .
                VALUES(?pa_type ?second_ind) { 
                    (bf:Production "0")
                    (bf:Publication "1")
                    (bf:Distribution "2")
                    (bf:Manufacture "3")
                } .
                OPTIONAL {
                    ?pa bf:place/rdfs:label ?a .
                }
                OPTIONAL {
                    ?pa bf:agent/rdfs:label ?b .
                }
                OPTIONAL {
                    FILTER EXISTS { ?pa bf:agent/rdfs:label ?b . } 
                    ?pa bf:date ?c .
                }
                
                BIND( "#" as ?first_ind ) .
                BIND( "264" as ?field ) .
            }
        """,
    },
    {
        "query": """
            SELECT DISTINCT ?field ?first_ind ?second_ind ?c 
            WHERE {
                ?instance bf:provisionActivity ?pa .
                ?pa a bf:Publication .
                ?pa bf:date ?c .
                FILTER NOT EXISTS { ?pa bf:agent/rdfs:label ?b . } 
                BIND( "#" as ?first_ind ) .
                BIND( "4" as ?second_ind ) .
                BIND( "264" as ?field ) .
            }
        """,
    },
    # 270
    {
        "note": """
            This will probably become more complex. Also not sure what happens if there are multiple dimensions.  
            There really shouldn't be.  That would be a new instance right? Could break this up into multiple queries, 
            one each per subfield.
            """,
        "query": """
            SELECT DISTINCT ?field ?a ?b ?c 
            WHERE {
                OPTIONAL {
                    ?instance bf:extent/rdfs:label ?a .
                }
                OPTIONAL {
                    ?instance bf:note ?note .
                    ?note bf:noteType "Physical details" .
                    ?note rdfs:label ?b .
                }
                OPTIONAL {
                    ?instance bf:dimensions ?c .
                }
                BIND( "300" as ?field ) .
            }
        """,
    },
    # 306-388
    {
        "note": "Series traced?  What happens? There are other subfields here too.",
        "query": """
            SELECT DISTINCT ?field ?first_ind ?a
            WHERE {
                ?instance bf:seriesStatement ?a .
                BIND( "0" as ?first_ind ) .
                BIND( "490" as ?field ) .
            }
        """,
    },
    {
        "note": "Should notes be on Work?  Is there a way to tell when?",
        "query": """
            SELECT DISTINCT ?field ?a
            WHERE {
                OPTIONAL {
                    ?instance bf:note ?note .
                    ?note rdfs:label ?a .
                    FILTER( NOT EXISTS{ ?note bf:noteType ?nt . } ) .
                }
                OPTIONAL {
                    ?work bf:hasInstance ?instance .
                    ?work bf:note ?note .
                    ?note rdfs:label ?a .
                    FILTER( NOT EXISTS{ ?note bf:noteType ?nt . } ) .
                }
                BIND( "500" as ?field ) .
            }
        """,
    },
    # 501-588
    {
        "note": """
            Does not handle NLM or NAL or other schemes.
        """,
        "query": """
            SELECT DISTINCT ?second_ind ?0 ?a ?atype ?sfs
            WHERE {
                ?work bf:hasInstance ?instance .
                ?work bf:subject ?subject .
                BIND( IF(isIRI(?subject), ?subject, "") as ?0 ) .
                BIND(
                    IF (EXISTS{?subject madsrdf:isMemberOfMADSScheme <http://id.loc.gov/authorities/childrensSubjects>},
                        "1",
                        IF (EXISTS{?subject madsrdf:isMemberOfMADSScheme <http://id.loc.gov/authorities/subjects>},
                            "0",
                            IF (EXISTS{?subject bf:source ?source . ?source bf:code ?source_code},
                                "7",
                                "4"
                            )
                        )
                    )
                as ?second_ind ) .
                OPTIONAL {
                    ?subject a madsrdf:ComplexSubject . 
                    ?subject madsrdf:componentList/rdf:first/madsrdf:authoritativeLabel ?a .
                    ?subject madsrdf:componentList/rdf:first/rdf:type ?atype .
                    {
                        SELECT ?subject (GROUP_CONCAT(?sfstr; SEPARATOR="--") AS ?sfs) WHERE {
                            ?subject madsrdf:componentList/rdf:rest*/rdf:first ?item .
                            {
                                SELECT *
                                WHERE {
                                    BIND(
                                        IF (EXISTS{?item a madsrdf:Topic},
                                            "dollar_x",
                                            IF (EXISTS{?item a madsrdf:GenreForm},
                                                "dollar_v",
                                                IF (EXISTS{?item a madsrdf:Geographic},
                                                    "dollar_z",
                                                    IF (EXISTS{?item a madsrdf:Temporal},
                                                        "dollar_y",
                                                        "unknown"
                                                    )
                                                )
                                            )
                                        )
                                    as ?sf ) .
                                    ?item madsrdf:authoritativeLabel ?label .
                                    BIND(CONCAT(?sf, ":", ?label) as ?sfstr ) .
                                }
                            }
                        }
                        GROUP BY ?subject     
                    }
                }
                OPTIONAL {
                    FILTER( NOT EXISTS { ?subject a madsrdf:ComplexSubject . } ) .
                    ?subject madsrdf:authoritativeLabel ?a .
                    ?subject a ?atype .
                    VALUES ?atype {  
                        madsrdf:Topic madsrdf:PersonalName madsrdf:CorporateName
                        madsrdf:ConferenceName madsrdf:Temporal madsrdf:Geographic
                    } .
                }
            }
        """,
        "process": "_process_lcsh_field"
    }
    
]