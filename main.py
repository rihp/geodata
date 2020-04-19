import os, datetime, json, requests
from dotenv import load_dotenv
from pymongo import MongoClient
import enricher, presenter, exporter
import argparse
import bson.json_util

load_dotenv()
presenter.say_hi()  # WELCOME MESSAGE

def parserFunction():
    # 02 - INSTRUCTIONS AND ARGUMENTS
    parser = argparse.ArgumentParser(description="Vesuvius is a retriever of satellite images. It currently uses a dataset containing volcanic eruptions and matches it with available photos from NASA's DSCOVR satellite, using the 'EPIC' API. The functionality of vesuvius has been desinged to be a modular program, in the sense that one could input a different dataset with relevant dates, and get the available satellite images from that date; Note that the DSCOVR satellite was launched into space on 2015, so older data will not be available. Also, very recent dates may not be available in the API's archive. DISCLAIMER: Use at your own risk.")
    parser.add_argument('lat', help="required latitude point to query. Type: float")
    parser.add_argument('lng', help="required latitude point to query. Type: float")
    parser.add_argument('--radius', help="Functionality under development; sets the radius to apply to the query.")
    parser.add_argument('--mailto', help="sends an email to the specified email.")
    parser.add_argument('--address', help="")
    #parser.add_argument('--version', help="displays vesuvius' version", )

    # 03 -PARSE ARGS AND CATCH ERRORS, like wrong lengths or formats
    args = parser.parse_args()
    latitude = float(args.lat)
    longitude = float(args.lng)

    """
    if type(longitude) is not float:
        print(type(longitude))
        raise ValueError('latitude must be a float')
    if args.lng is not float: # | (int(args.month) > 12)):
        print(type(longitude))
        raise ValueError('longitude must be a float')
    """
    return args
args = parserFunction()


print(f'{args.lat},{args.lng}')
address = 'Maldives Islands'
#coords = enricher.geocode(address)

# I have to make a function to melt Geopoints into 4SQ `ll` format
# This will be the cluster points generated from the crunchbase dataset
#ll = coords
#ll = f"{ll['coordinates'][1]},{ll['coordinates'][0]}"
#ll = '40.37417177212408,-3.7015647782170413' # Madrid
#ll ='40.7243,-74.0018' # NYC
ll = f'{args.lat},{args.lng}' # use parsed args


# STEP 2: Define categories to query
#   INPUT : list of categories which will be funnelled
#   OUTPUT:  output as GeoPoints (all cleaned, and loop again here.)
kids_points = ['daycare']
party_points = ['convention center', 'nightlife spot']
flight_points = ['airport', 'heliport']

relevant_categories = [kids_points,
                    #party_points,
                    flight_points]


# Call the new functions
print(f'~ Exporting to json this relevant_categories: {relevant_categories}')
for category_set in relevant_categories:
    #category_set = flight_points
    print(f'~ Looping this category_set: {category_set}')
    category_set_cluster = enricher.cluster_request(ll, category_set)

    exporter.to_json(category_set, category_set_cluster)

    print(f'~ exporter.to_MongoDB(category_set, category_set_cluster): {category_set}')
    exporter.to_MongoDB(category_set, category_set_cluster)


# Now exporting some of that data to a json
client = MongoClient('mongodb://localhost/companies')
db = client.companies
collection = db.geo_data

print(' Exporting the MongoDB collection to Output folder ~')
cursor = collection.find({})
file = open("OUTPUT/geo_data.json", "w")
file.write('[')
for document in cursor:
    file.write(bson.json_util.dumps(document))
    file.write(',')
file.write(']')


print(' see you again soon ~')