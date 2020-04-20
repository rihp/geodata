from pymongo import MongoClient
import enricher
import subprocess


client = MongoClient('mongodb://localhost/companies')
db = client.companies
collection = db.geo_one
cur = collection.find({})
query = list(cur)

for venue in query[0:25]:
    try: 
        coords = venue['venue_location']['GeoPoint']['coordinates']
        print(f"{coords[0]},{coords[1]}")
        subprocess.call(f'python3 main.py {coords[1]} {coords[0]}', shell=True)
    except Exception as e:
        print(e)