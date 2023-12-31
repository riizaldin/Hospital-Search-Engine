import re
from flask import Flask, render_template, redirect, request
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
import requests
from operator import itemgetter
from geopy.geocoders import Nominatim
from flask import jsonify


def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of Earth in kilometers
    return distance
def remove_prefix(query):
    # Define patterns to match "rs " or "rumah sakit " at the beginning of the string
    pattern = r'^(rs |rumah\s*sakit\s*)'

    # Use re.sub to remove the matched pattern if it exists at the beginning of the string
    result = re.sub(pattern, '', query)

    return result

sparql = SPARQLWrapper(
    "http://localhost:3030/sumutsehat/query"
)

app = Flask(__name__)


@app.route('/')
def index():
    all_hospitals = get_all_hospitals()
    return render_template("index.html", all_hospitals = all_hospitals)

@app.route('/search', methods=['GET'])
def search():
    all_hospitals = get_all_hospitals()
    search_query = request.args.get('search')
    if search_query is None:
        return redirect('/')
    changed_query = remove_prefix(search_query)
    sparqlQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?subject ?nama ?alamat ?kelas ?luas_bangunan ?kota ?luas_tanah ?blu ?jenis ?telepon ?image_url (GROUP_CONCAT(?pelayanan; separator=',') AS ?listPelayanan)
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
        OPTIONAL {{ ?subject schema:kota ?kota . }}
        OPTIONAL {{ ?subject schema:image_url ?image_url . }}
        FILTER (CONTAINS(LCASE(?nama), LCASE("{changed_query}")) || CONTAINS(LCASE(?alamat), LCASE("{search_query}")) || CONTAINS(LCASE(?pelayanan), LCASE("{search_query}")))
    }}
    GROUP BY ?subject ?nama ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?kota
    HAVING (BOUND(?nama))
    """
    sparql.setQuery(sparqlQuery)
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    result = ret["results"]["bindings"]
    count = len(result)
    return render_template("search.html", result=result, search_query=search_query, count=count, all_hospitals = all_hospitals)

@app.route('/detail/<hospital>')
def detail(hospital):
    all_hospitals = get_all_hospitals()
    sparqlQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT  ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur ?koordinat ?kota (GROUP_CONCAT(?pelayanan; separator=',') AS ?listPelayanan)
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
    GROUP BY  ?subject ?alamat ?kelas ?luas_bangunan ?luas_tanah ?blu ?jenis ?telepon ?image_url ?direktur ?koordinat ?kota
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

    kamarQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?kelas_tempat ?kapasitas
    WHERE {{
        ?subject schema:name "{hospital}".
        ?subject schema:tempat_tidur ?tempat_tidur .
        ?tempat_tidur schema:kelas_tempat ?kelas_tempat .
        ?tempat_tidur schema:kapasitas ?kapasitas .
    }}
    """
    sparql.setQuery(kamarQuery)
    sparql.setReturnFormat(JSON)
    ret_kamar = sparql.queryAndConvert()
    result_kamar = ret_kamar["results"]["bindings"] 
    kamar = []     
    for each_result in result_kamar:
        row_data = {
            "kelas_tempat": each_result.get("kelas_tempat", {}).get("value", ""),
            "kapasitas": each_result.get("kapasitas", {}).get("value", ""),
        }
        kamar.append(row_data)

    tenagaQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?grup ?sdm ?jumlah
    WHERE {{
        ?subject schema:name "{hospital}".
        ?subject schema:tenaga ?tenaga .
        ?tenaga schema:grup ?grup .
        ?tenaga schema:sdm ?sdm .
        ?tenaga schema:jumlah ?jumlah .
    }}
    """
    sparql.setQuery(tenagaQuery)
    sparql.setReturnFormat(JSON)
    ret_tenaga = sparql.queryAndConvert()
    result_tenaga = ret_tenaga["results"]["bindings"]
    tenaga = []
    for each_result in result_tenaga:
        row_data = {
            "grup": each_result.get("grup", {}).get("value", ""),
            "sdm": each_result.get("sdm", {}).get("value", ""),
            "jumlah": each_result.get("jumlah", {}).get("value", "")
        }
        tenaga.append(row_data)
    koordinat = result[0]['koordinat']['value']
    koordinat = koordinat.split(',')
    latitude_rs = koordinat[0]
    longitude_rs = koordinat[1]
    allQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?subject ?koordinat ?nama ?alamat ?telepon ?image_url
    WHERE {{
        ?subject schema:name ?nama .
        OPTIONAL {{ ?subject schema:alamat ?alamat . }}
        OPTIONAL {{ ?subject schema:telepon ?telepon . }}
        OPTIONAL {{ ?subject schema:image_url ?image_url . }}
        ?subject schema:koordinat ?koordinat .
    }}
    GROUP BY ?subject ?alamat ?telepon ?image_url ?koordinat ?nama
    HAVING (BOUND(?nama))
    """

    sparql.setQuery(allQuery)
    sparql.setReturnFormat(JSON)
    all = sparql.queryAndConvert()
    all_hospital = all["results"]["bindings"]

    coordinates_dict = {}

    for data in all_hospital:
        if data.get('koordinat') and data['koordinat'].get('value'):
            koordinat = data['koordinat']['value']
            koordinat = koordinat.split(',')
            latitude = koordinat[0]
            longitude = koordinat[1]
            
            if data.get('nama') and data['nama'].get('value'):
                name = data['nama']['value']
                coordinates_dict[name] = [latitude, longitude]

    if result[0]['koordinat'] and result[0]['koordinat'].get('value'):
        koordinat = result[0]['koordinat']['value']
        latitude_1, longitude_1 = map(float, koordinat.split(','))
    else:
        latitude_1 = None
        longitude_1 = None

    # Calculate distances and store in a dictionary along with names using Haversine formula
    distances_dict = {}
    for name, coords in coordinates_dict.items():
        lat2, lon2 = map(float, coords)
        distance = haversine_distance(latitude_1, longitude_1, lat2, lon2)
        formatted_distance = round(distance, 2)
        distances_dict[name] = formatted_distance

    sorted_distances = sorted(distances_dict.items(), key=itemgetter(1))[:4]

    # Extract the names of the three closest hospitals
    closest_hospitals = [name for name, _ in sorted_distances]

    # Fetch details for the three closest hospitals
    closest_hospitals_details = []
    for name, distance in sorted_distances:
        if name != hospital:  # Replace 'current_hospital_name' with the name of the current hospital
            for data in all_hospital:
                if data.get('nama') and data['nama']['value'] == name:
                    hospital_details = {
                        'dat': data,  # Assuming 'dat' holds the entire hospital details
                        'distance': distance
                    }
                    closest_hospitals_details.append(hospital_details)
                    break  # Stop searching once the hospital details are found

        if len(closest_hospitals_details) == 3:  # Stop fetching once three hospitals are found
            break

    return render_template("detail.html", all_hospitals=all_hospitals, kamar=kamar, tenaga=tenaga, result=result, name=hospital, coordinates=coordinates_dict, distances=distances_dict, closest_hospitals_details=closest_hospitals_details, latitude = latitude_rs, longitude = longitude_rs)


@app.route('/kota/<kota>')
def about(kota):
    all_hospitals = get_all_hospitals()
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
    return render_template("kota.html", all_hospitals=all_hospitals, wikiResult=wikiResult, latitude=latitude, longitude=longitude, tanggal=tanggal)

latitude_now = 0
longitude_now = 0
@app.route('/getLocation', methods=["POST"])
def get_location():
    global latitude_now, longitude_now

    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    latitude_now = latitude
    longitude_now = longitude

    # Call a function to calculate distances and retrieve closest hospitals
    closest_hospitals_details = get_closest_hospitals(latitude, longitude)

    return jsonify(closest_hospitals_details)

def get_all_hospitals():
    allQuery = f"""
    PREFIX schema: <http://websemantikkelompok6.org/>
    SELECT ?subject ?koordinat ?nama ?alamat ?telepon ?image_url
    WHERE {{
        ?subject schema:name ?nama .
        OPTIONAL {{ ?subject schema:alamat ?alamat . }}
        OPTIONAL {{ ?subject schema:telepon ?telepon . }}
        OPTIONAL {{ ?subject schema:image_url ?image_url . }}
        ?subject schema:koordinat ?koordinat .
    }}
    GROUP BY ?subject ?alamat ?telepon ?image_url ?koordinat ?nama
    HAVING (BOUND(?nama))
    """

    sparql.setQuery(allQuery)
    sparql.setReturnFormat(JSON)
    all = sparql.queryAndConvert()
    all_hospital = all["results"]["bindings"]
    return all_hospital

def get_closest_hospitals(user_latitude, user_longitude):
    all_hospital = get_all_hospitals()
    coordinates_dict = {}
    for data in all_hospital:
        if data.get('koordinat') and data['koordinat'].get('value'):
            koordinat = data['koordinat']['value']
            koordinat = koordinat.split(',')
            latitude = koordinat[0]
            longitude = koordinat[1]
            
            if data.get('nama') and data['nama'].get('value'):
                name = data['nama']['value']
                coordinates_dict[name] = [latitude, longitude]

    distances_dict = {}
    for name, coords in coordinates_dict.items():
        lat2, lon2 = map(float, coords)
        distance = haversine_distance(user_latitude, user_longitude, lat2, lon2)
        distances_dict[name] = distance

    sorted_distances = sorted(distances_dict.items(), key=itemgetter(1))[:4]
    closest_hospitals_details = []
    for name, distance in sorted_distances:
        for data in all_hospital:
            if data.get('nama') and data['nama']['value'] == name:
                hospital_details = {
                    'data': data,
                    'distance': distance
                }
                closest_hospitals_details.append(hospital_details)
                break 

        if len(closest_hospitals_details) == 4:
            break

    return closest_hospitals_details

if __name__ == '__main__':
    app.run(debug=True)
  