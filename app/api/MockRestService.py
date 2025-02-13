from datetime import timedelta
import time
from timeloop import Timeloop
from fastapi import APIRouter, Response
from rdflib import ConjunctiveGraph
from rdflib_endpoint import SparqlRouter

tag = "mock"
tl = Timeloop()
g = ConjunctiveGraph()

router = APIRouter(
    prefix="/mock",
    tags=[tag]
)

tag_metadata = {
    "name": tag,
    "description": "Mock endpoint which returns a modified snippet of dbpedia dataset which updates every nanosecond to simulate fast changing data",
}

sparql_router = SparqlRouter(
    graph=g,
    path="/mock/sparql",
    # Metadata used for the SPARQL service description and Swagger UI:
    title="SPARQL endpoint for mock graph",
    description="A SPARQL endpoint to serve mock data to test/evaluate polling tasks",
    version="0.1.0"
)

@tl.job(interval=timedelta(seconds=2))
def update_mock_data(g = g):
    g -= g.triples((None, None, None))
 
    data = """<http://de.dbpedia.org/resource/Österreich> <http://dbpedia.org/ontology/areaTotal> "1.12E8"^^<http://www.w3.org/2001/XMLSchema#double> . 
<http://de.dbpedia.org/resource/Österreich> <http://dbpedia.org/ontology/topLevelDomain> <http://de.dbpedia.org/resource/.at> . 
<http://de.dbpedia.org/resource/Österreich> <http://dbpedia.org/ontology/populationTotal> "{:population}"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger> . 
<http://de.dbpedia.org/resource/Österreich> <http://dbpedia.org/ontology/abstract> "Österreich ( [ˈøːstɐʁaɪ̯ç]; amtlich Republik Österreich) ist ein mitteleuropäischer Binnenstaat mit rund 8,9 Millionen Einwohnern. Die angrenzenden Staaten sind Deutschland und Tschechien im Norden, die Slowakei und Ungarn im Osten, Slowenien und Italien im Süden sowie die Schweiz und Liechtenstein im Westen. Österreich ist ein demokratischer und föderaler Bundesstaat, im Besonderen eine semipräsidentielle Republik. Seine großteils aus den historischen Kronländern hervorgegangenen neun Bundesländer sind das Burgenland, Kärnten, Niederösterreich, Oberösterreich, Salzburg, die Steiermark, Tirol, Vorarlberg und Wien. Das Bundesland Wien ist zugleich Bundeshauptstadt und auch einwohnerstärkste Stadt des Landes. Weitere Bevölkerungszentren sind Graz, Linz, Salzburg und Innsbruck. Das Land wird von der Böhmischen Masse und der Thaya im Norden, den Karawanken und dem Steirischen Hügelland im Süden, der Pannonischen Tiefebene im Osten sowie dem Rhein und dem Bodensee im Westen begrenzt. Mehr als 62 Prozent seiner Staatsfläche werden von alpinem Hochgebirge gebildet. Der österreichische Staat wird deshalb auch als Alpenrepublik bezeichnet. Die Bezeichnung Österreich ist in ihrer althochdeutschen Form Ostarrichi erstmals aus dem Jahr 996 überliefert. Daneben war ab dem frühen Mittelalter die lateinische Bezeichnung Austria in Verwendung. Ursprünglich eine Grenzmark des Stammesherzogtums Baiern, wurde Österreich 1156 zu einem im Heiligen Römischen Reich eigenständigen Herzogtum erhoben. Nach dem Aussterben des Geschlechts der Babenberger 1246 setzte sich das Haus Habsburg im Kampf um die Herrschaft in Österreich durch. Das als Österreich bezeichnete Gebiet umfasste später die gesamte Habsburgermonarchie sowie in der Folge das 1804 konstituierte Kaisertum Österreich und die österreichische Reichshälfte der 1867 errichteten Doppelmonarchie Österreich-Ungarn. Die heutige Republik entstand ab 1918, nach dem für Österreich-Ungarn verlorenen Ersten Weltkrieg, aus den zunächst Deutschösterreich genannten deutschsprachigen Teilen der Monarchie. Mit dem Vertrag von Saint-Germain wurden die Staatsgrenze und der Name Republik Österreich festgelegt. Damit einher ging der Verlust Südtirols. Die Erste Republik war von innenpolitischen Spannungen geprägt, die in einen Bürgerkrieg und die Ständestaatsdiktatur mündeten. Durch den sogenannten „Anschluss“ stand das Land ab 1938 unter nationalsozialistischer Herrschaft. Nach der Niederlage des Deutschen Reiches im Zweiten Weltkrieg wieder ein eigenständiger Staat, erklärte Österreich am Ende der alliierten Besatzung 1955 seine immerwährende Neutralität und trat den Vereinten Nationen bei. Österreich ist seit 1956 Mitglied im Europarat, Gründungsmitglied der 1961 errichteten Organisation für wirtschaftliche Zusammenarbeit und Entwicklung (OECD) und seit 1995 ein Mitgliedsstaat der Europäischen Union."@de .""" 


    g.parse(data=data.replace("{:population}", str(time.time_ns())))
    g.commit()
    

@router.get("/n-triples.nt")
async def get_rdf_mock_austria():
    return Response(content=g.serialize(format="nt"), media_type="application/n-triples")