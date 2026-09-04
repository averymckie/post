CREATE NODE TABLE Event(id STRING, lemma STRING, obligatory BOOLEAN, negated BOOLEAN, sentence STRING, PRIMARY KEY(id))
CREATE NODE TABLE Arg(id STRING, quote STRING, PRIMARY KEY(id))
CREATE REL TABLE AGENT(FROM Event TO Arg)
CREATE REL TABLE PATIENT(FROM Event TO Arg)
CREATE REL TABLE THEME(FROM Event TO Arg)
CREATE REL TABLE PRECEDES(FROM Event TO Event)
MATCH (e:Event)-[:AGENT]->(x:Arg) WHERE e.obligatory RETURN e.id, e.lemma, x.quote ORDER BY e.id
MATCH (a:Event)-[:PRECEDES]->(b:Event) RETURN a.lemma, b.lemma, a.id, b.id ORDER BY a.id, b.id
