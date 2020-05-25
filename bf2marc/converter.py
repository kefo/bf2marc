import sys
import json

from copy import deepcopy

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.stores import sparqlstore
from SPARQLWrapper import SPARQLWrapper, POST, TURTLE, JSON

from pymarc import Record, Field

class Converter:
    
    _prefixblock = """
            PREFIX bf: <http://id.loc.gov/ontologies/bibframe/> 
            PREFIX bflc: <http://id.loc.gov/ontologies/bflc/>
            PREFIX madsrdf: <http://www.loc.gov/mads/rdf/v1#>
            PREFIX iddatatypes: <http://id.loc.gov/datatypes/edtf>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            """
    
    def __init__(
        self,
        config
    ) -> None:
        self.config = config
        self._g = Graph()
        self.set_profile()
        self.records = []
        return None

    def load(
        self,
        rdfdata: str = '',
        rdffile: str = '',
        rdfformat: str = "xml"
    ) -> None:
        if rdffile != "":
            self._g.parse(rdffile, format=rdfformat)
        else:
            self._g.parse(rdfdata, format=rdfformat)

        self._SWUpdate = SPARQLWrapper(self.config["sparql_update"])
        #self._SWUpdate.setHTTPAuth(DIGEST)
        #self._SWUpdate.setCredentials("login", "password")
        self._SWUpdate.setMethod(POST)
        self._SWUpdate.setReturnFormat(JSON)
        
        triples = self._g.serialize(format='nt')
        #print(triples)
        #sys.exit(0)
        triples = triples.decode("utf-8")
        insert_query = """
            INSERT DATA {
                %TRIPLES%
            }
            """
        query = insert_query.replace("%TRIPLES%", triples)
        self._SWUpdate.setQuery(self._prefixblock + query)
        try:
            results = self._SWUpdate.query()
        except:
            raise
        return None    

    def convert(
        self
    ) -> None:
        self._SWSelect = SPARQLWrapper(self.config["sparql_select"])
        #self._SWUpdate.setHTTPAuth(DIGEST)
        #self._SWUpdate.setCredentials("login", "password")
        self._SWSelect.setMethod(POST)
        self._SWSelect.setReturnFormat(JSON)
        
        query = """
            SELECT DISTINCT ?instance
            WHERE {
                OPTIONAL {
                    ?w bf:hasInstance ?instance .
                }
                OPTIONAL {
                    ?instance bf:isInstanceOf ?w .
                }
            }
            """
        
        self._SWSelect.setQuery(self._prefixblock + query)
        results = self._SWSelect.query()
        results = results.response.read()
        result = json.loads(results.decode("utf-8"))
        
        instances = []
        for row in result["results"]["bindings"]:
            if "instance" in row:
                instances.append(row["instance"]["value"])
        
        for i in instances:
            record = Record()
            record.add_field(
                Field(
                    tag = "001",
                    data = i
                )
            )
            for field in self._profile:
                record = self._process_field(i, field, record)
            print(record)
            self.records.append(record)

        return None
        
    def set_profile(
        self,
        use_profile: str = 'bfdr'
    ) -> None:
        if type(use_profile) is str:
            if use_profile == "bfdr":
                from bf2marc.profiles.bfdr import profile
                self._profile = profile
            elif use_profile == "lc":
                from bf2marc.profiles.lc import profile
                self._profile = profile
            else:
                raise
        else:
            # Assume profile object
            self._profile = use_profile
        return None
                
    def unload(
        self
    ) -> None:
        delete_query = """
            DELETE { ?s ?p ?o }
            WHERE {
                ?s ?p ?o 
            }
            """
        self._SWUpdate.setQuery(self._prefixblock + delete_query)
        try:
            results = self._SWUpdate.query()
        except:
            raise
        return None
        
    def _process_lcsh_field(
        self,
        record,
        fielddata
    ) -> Record:
        print(fielddata)

        for f in fielddata:
            newf = deepcopy(f)
            subfields = []
            if '0' in f:
                subfields.append("0")
                subfields.append(f["0"]["value"])
            if 'a' in f:
                subfields.append("a")
                subfields.append(f["a"]["value"])
            for sf in f:
                if sf == "atype":
                    atype = f[sf]["value"]
                    newf["field"] = {}
                    newf["first_ind"] = {}
                    # Have to review first indicator values here.
                    if atype == "http://www.loc.gov/mads/rdf/v1#PersonalName":
                        newf["field"]["value"] = "600"
                        newf["first_ind"]["value"] = "1"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#CorporateName":
                        newf["field"]["value"] = "610"
                        newf["first_ind"]["value"] = "2"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#ConferenceName":
                        newf["field"]["value"] = "611"
                        newf["first_ind"]["value"] = "2"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#Title":
                        newf["field"]["value"] = "630"
                        newf["first_ind"]["value"] = "0"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#Temporal":
                        newf["field"]["value"] = "648"
                        newf["first_ind"]["value"] = "#"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#Topic":
                        newf["field"]["value"] = "650"
                        newf["first_ind"]["value"] = "#"
                    elif atype == "http://www.loc.gov/mads/rdf/v1#Geographic":
                        newf["field"]["value"] = "651"
                        newf["first_ind"]["value"] = "#"
                if sf == "sfs":
                    sfparts = f[sf]["value"].split('--')
                    sfparts.reverse()
                    for sfp in sfparts[1:None]:
                        parts = sfp.split(':')
                        sf = parts[0].replace('dollar_', '')
                        d = ":".join(parts[1:None])
                        subfields.append(sf)
                        subfields.append(d)
        
            if len(subfields) > 0:
                record.add_field(
                    Field(
                        tag = newf["field"]["value"],
                        indicators = [newf["first_ind"]["value"], newf["second_ind"]["value"]],
                        subfields = subfields
                    )
                )
        return record
        
    def _process_standard(
        self,
        record,
        fielddata
    ) -> Record:
        for f in fielddata:
            if int(f["field"]["value"]) < 10:
                data = ""
                for sf in f:
                    if sf != "field" and sf != "first_ind" and sf != "second_ind":
                        data += f[sf]["value"]
                if data != "":
                    record.add_field(
                        Field(
                            tag = f["field"]["value"],
                            data = data
                        )
                    )
            else:
                subfields = []
                for sf in f:
                    if sf != "field" and sf != "first_ind" and sf != "second_ind":
                        subfields.append(sf)
                        subfields.append(f[sf]["value"])
                if len(subfields) > 0:
                    record.add_field(
                        Field(
                            tag = f["field"]["value"],
                            indicators = [f["first_ind"]["value"], f["second_ind"]["value"]],
                            subfields = subfields
                        )
                    )
        return record
        
    def _process_field(
        self,
        instance,
        field,
        record
    ) -> None:
        query = field["query"]
        query = query.replace('?instance', '<' + instance + '>')
        
        self._SWSelect.setQuery(self._prefixblock + query)
        results = self._SWSelect.query()
        results = results.response.read()
        result = json.loads(results.decode("utf-8"))
        
        # print(result)
        result_vars = []
        for v in result["head"]["vars"]:
            result_vars.append(str(v))
        
        fielddata = []
        for row in result["results"]["bindings"]:
            subfielddata = {}
            for r in result_vars:
                if r in row and row[r] != None:
                    subfielddata[r] = row[r]
            if "first_ind" not in subfielddata:
                subfielddata["first_ind"] = {}
                subfielddata["first_ind"]["value"] = "#"
            if "second_ind" not in subfielddata:
                subfielddata["second_ind"] = {}
                subfielddata["second_ind"]["value"] = "#"
            fielddata.append(subfielddata)
            
        if "process" in field:
            fn = getattr(self, field["process"])
            record = fn(record, fielddata)
        else:
            self._process_standard(record, fielddata)
        
        return record
