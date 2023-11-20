from flask import Flask, render_template, redirect, request
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

sparql = SPARQLWrapper(
    "http://localhost:3030/sumutsehat/query"
)

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search')
    if search_query is None:
        return redirect('/')
    sparqlQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?subject ?nama ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url (GROUP_CONCAT(?pelayanan; separator=',') AS ?listPelayanan)
    WHERE {{
        ?subject schema:name ?nama .
        OPTIONAL {{ ?subject schema:alamat ?alamat . }}
        OPTIONAL {{ ?subject schema:kelas ?kelas . }}
        OPTIONAL {{ ?subject schema:luas_bangunan ?luas_bangunan . }}
        OPTIONAL {{ ?subject schema:luas_tanah ?luas_tanah . }}
        OPTIONAL {{ ?subject schema:blu ?blu . }}
        OPTIONAL {{ ?subject schema:jenis ?jenis . }}
        OPTIONAL {{ ?subject schema:pelayanan ?pelayanan . }}
        OPTIONAL {{ ?subject schema:telepon ?telepon . }}
        OPTIONAL {{ ?subject schema:image_url ?image_url . }}
        FILTER (CONTAINS(LCASE(?nama), LCASE("{search_query}")) || CONTAINS(LCASE(?alamat), LCASE("{search_query}")))
    }}
    GROUP BY ?subject ?nama ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url
    HAVING (BOUND(?nama))
    """
    sparql.setQuery(sparqlQuery)
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    result = ret["results"]["bindings"]
    count = len(result)
    return render_template("search.html", result=result, search_query=search_query, count=count)

@app.route('/detail/<hospital>')
def detail(hospital):
    sparqlQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur (GROUP_CONCAT(?pelayanan; separator=',') AS ?listPelayanan)
    WHERE {{
        ?subject schema:name "{hospital}".
        OPTIONAL {{ ?subject schema:alamat ?alamat . }}
        OPTIONAL {{ ?subject schema:kelas ?kelas . }}
        OPTIONAL {{ ?subject schema:luas_bangunan ?luas_bangunan . }}
        OPTIONAL {{ ?subject schema:luas_tanah ?luas_tanah . }}
        OPTIONAL {{ ?subject schema:blu ?blu . }}
        OPTIONAL {{ ?subject schema:jenis ?jenis . }}
        OPTIONAL {{ ?subject schema:pelayanan ?pelayanan . }}
        OPTIONAL {{ ?subject schema:direktur ?direktur .}}
        OPTIONAL {{ ?subject schema:telepon ?telepon . }}
        OPTIONAL {{ ?subject schema:image_url ?image_url . }}
    }}
    GROUP BY ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur
    """
    sparql.setQuery(sparqlQuery)
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    result = ret["results"]["bindings"]
    for data in result:
        if data.get('listPelayanan') and data['listPelayanan'].get('value'):
            services_string = data['listPelayanan']['value']
            data['listPelayanan']['value'] = services_string.split(',')

    randomQuery = f"""
        PREFIX schema: <http://websemantikkelompok6.org/>
        SELECT DISTINCT ?subject ?nama ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url
        WHERE {{
            ?subject schema:name ?nama .
            OPTIONAL {{ ?subject schema:alamat ?alamat . }}
            OPTIONAL {{ ?subject schema:kelas ?kelas . }}
            OPTIONAL {{ ?subject schema:luas_bangunan ?luas_bangunan . }}
            OPTIONAL {{ ?subject schema:luas_tanah ?luas_tanah . }}
            OPTIONAL {{ ?subject schema:blu ?blu . }}
            OPTIONAL {{ ?subject schema:jenis ?jenis . }}
            OPTIONAL {{ ?subject schema:pelayanan ?pelayanan . }}
            OPTIONAL {{ ?subject schema:telepon ?telepon . }}
            OPTIONAL {{ ?subject schema:image_url ?image_url . }}
        }}
        ORDER BY RAND()
        LIMIT 3
        """
    sparql.setQuery(randomQuery)
    sparql.setReturnFormat(JSON)
    rand = sparql.queryAndConvert()
    random = rand["results"]["bindings"]

    wikidataQuery = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bd: <http://www.bigdata.com/rdf#>

    SELECT ?hospitals ?label ?coordinates WHERE{{
        ?hospitals wdt:P31 wd:Q16917 .
        ?hospitals wdt:P131 wd:Q5972 .
        ?hospitals  rdfs:label ?label .
        OPTIONAL {{?hospitals wdt:P625 ?coordinates .}} 
        FILTER (langMatches( lang(?label), "id" ) ) . 
    }}
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    # response = requests.post("https://query.wikidata.org/sparql", {"query":wikidataQuery}, headers=headers)
    # response_json = response.json()
    # wikiResult =  response_json["results"]["bindings"]

    # 9f26ee5b5fda4b5ba51ca2b4afebb031
    return render_template("detail.html", result=result, name=hospital, random=random)


if __name__ == '__main__':
    app.run(debug=True)
  