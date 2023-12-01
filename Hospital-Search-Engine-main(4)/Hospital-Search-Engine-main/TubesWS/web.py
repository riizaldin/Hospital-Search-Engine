from flask import Flask, render_template, redirect, request
from datetime import datetime
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
        FILTER (CONTAINS(LCASE(?nama), LCASE("{search_query}")) || CONTAINS(LCASE(?alamat), LCASE("{search_query}")) || CONTAINS(LCASE(?pelayanan), LCASE("{search_query}")))
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
    SELECT ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur ?koordinat ?kota (GROUP_CONCAT(?pelayanan; separator=',') AS ?listPelayanan)
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
        ?subject schema:kota ?kota .
        ?subject schema:koordinat ?koordinat .
    }}
    GROUP BY ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur ?koordinat ?kota
    """
    sparql.setQuery(sparqlQuery)
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    result = ret["results"]["bindings"]
    for data in result:
        if data.get('listPelayanan') and data['listPelayanan'].get('value'):
            services_string = data['listPelayanan']['value']
            data['listPelayanan']['value'] = services_string.split(',')
    koordinat = result[0]['koordinat']['value']
    koordinat = koordinat.split(',')
    latitude = koordinat[0]
    longitude = koordinat[1] 
    randomQuery = f"""
        PREFIX schema: <http://websemantikkelompok6.org/>
        SELECT DISTINCT ?subject ?nama ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url
        WHERE {{
            ?subject schema:name ?nama .
            FILTER (STRLEN(?nama) > 0) .
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

    return render_template("detail.html", result=result, name=hospital, random=random, latitude=latitude, longitude=longitude)

@app.route('/kota/<kota>')
def about(kota):
    kodeKota = {
        "Deli Serdang": "Q5804" ,
        "Tapanuli Utara": "Q5863" ,
        "Kota Gunungsitoli": "Q5967" ,
        "Serdang Bedagai": "Q5899" ,
        "Padang Lawas Utara": "Q5857" ,
        "Kota Tanjung Balai": "Q5987" ,
        "Labuhan Batu Selatan": "Q5905" ,
        "Tapanuli Selatan": "Q5914" ,
        "Nias Barat": "Q5909" ,
        "Langkat": "Q5833" ,
        "Kota Medan": "Q5972" ,
        "Pakpak Bharat": "Q5872" ,
        "Kota Tebing Tinggi": "Q5989" ,
        "Tapanuli Tengah": "Q5800" ,
        "Padang Lawas": "Q5866" ,
        "Nias Selatan": "Q5918" ,
        "Kota Binjai": "Q5954" ,
        "Mandailing Natal": "Q5837" ,
        "Humbang Hasundutan": "Q5808" ,
        "Batu Bara": "Q5797" ,
        "Simalungun": "Q5903" ,
        "Toba Samosir": "Q5911" ,
        "Labuhan Batu": "Q5814" ,
        "Samosir": "Q5888" ,
        "Nias Utara": "Q5853" ,
        "Karo": "Q5810" ,
        "Kota Padang Sidempuan": "Q5974" ,
        "Asahan": "Q1795" ,
        "Kota Pematang Siantar": "Q5979" ,
        "Nias": "Q5841" ,
        "Dairi": "Q5801" ,
        "Kota Sibolga": "Q5984" ,
        "Labuhan Batu Utara": "Q5842" ,
    }
    for city in kodeKota:
        if city == kota:
            kode = kodeKota[kota]
    wikidata = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX bd: <http://www.bigdata.com/rdf#>

        SELECT ?label ?nama ?koordinat ?tanggal_lahir ?populasi ?area ?kode_pos ?website ?logo ?gambar WHERE{{
            wd:{kode}  rdfs:label ?label .
            OPTIONAL {{ wd:{kode} wdt:P1448 ?nama . }}
            OPTIONAL {{ wd:{kode} wdt:P625 ?koordinat . }}
            OPTIONAL {{ wd:{kode} wdt:P571 ?tanggal_lahir . }}
            OPTIONAL {{ wd:{kode} wdt:P1082 ?populasi . }}
            OPTIONAL {{ wd:{kode} wdt:P2046 ?area . }}
            OPTIONAL {{ wd:{kode} wdt:P281 ?kode_pos . }}
            OPTIONAL {{ wd:{kode} wdt:P856 ?website . }}
            OPTIONAL {{ wd:{kode} wdt:P158 ?logo . }}
            OPTIONAL {{ wd:{kode} wdt:P94 ?logo .}}

            OPTIONAL {{ wd:{kode} wdt:P18 ?gambar . }}
            FILTER (langMatches( lang(?label), "id" ) ) . 
        }}
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    response = requests.post("https://query.wikidata.org/sparql", data={"query": wikidata}, headers=headers)
    response_json = response.json()
    wikiResult =  response_json["results"]["bindings"]
    if 'koordinat' in wikiResult[0]:
        koordinat = wikiResult[0]['koordinat']['value'].replace('Point(', '').replace(')', '')
        longitude, latitude = koordinat.split(' ')

    if 'tanggal_lahir' in wikiResult[0]:
        iso_date_time = wikiResult[0]['tanggal_lahir']['value']
        tanggal = datetime.fromisoformat(iso_date_time[:-1])
        tanggal = tanggal.strftime("%Y-%m-%d")
    else:
        tanggal = None
    return render_template("kota.html", wikiResult=wikiResult, latitude=latitude, longitude=longitude, tanggal=tanggal)

if __name__ == '__main__':
    app.run(debug=True)
  