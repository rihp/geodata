import os, datetime, json, requests
from dotenv import load_dotenv
from pymongo import MongoClient
import enricher, presenter
import argparse

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

# Call the new function
for category_set in relevant_categories:
    #category_set = flight_points
    print(f'~ Looping this category_set: {category_set}')
    category_set_cluster = enricher.cluster_request(ll, category_set)

    # Exporter.py module
    def to_json(category_set):
        """
        ♠ OPTIMIZATION: refactor this for loop into a function
            It should actually take different `category_set`s 
            and from them generate the appropiate .json 
            OUTPUT documents. 
                    #Exports the places to a file.json
        """
        print(" ~ Exporting unwinded raw data to OUTPUT/ folder")
        for key in category_set:
            print(f" ~ Printing key: {key}")
            response = category_set_cluster[key]
            with open(f'OUTPUT/{key}-raw.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(),f, ensure_ascii=False, indent=4)
                    
            #print(f"{response.json()}")
            print(f"{type(response)}")
            #print(f" ~ Printing response.json():")
        print(f'~ Looping this category_set: {category_set}')
    print(f'~ Exporting to json this category_set: {category_set}')

    to_json(category_set)

    ##################################
    #################################
    #        
    #    IMPORTANT STEP !!!
    #     Formatting the output data
    #
    def GeopointFrom4SQ(venue):
        """
        INPUT: 
        - A single FourSquare API venue `blob`
        OUTPUT:
        - A correctly formatted `blob` for future use and export downstream
        """
        loc = venue['location']
        return {'name':venue['name'],
                'GeoPoint':{
                    'type':'Point',
                    'PointCategory':'4square location',      
                    'coordinates':[
                        loc['lng'],
                        loc['lat']
                    ]
                },
                #'category':venue['categories'][0]['name'], 
                'categories':venue['categories'],
                'formattedAddress':venue['location']['formattedAddress']
        }

    def venues_to_GeoPoints(venues):
        """
        INPUT
        - Foursquare API venues `blob`
        OUTPUT
        - An ITERATOR with formatted dicts with key:value pairs, to be sent to MongoDB
        """
        for venue in venues:
            print(venue)
            #print(GeopointFrom4SQ(venue))            
            yield GeopointFrom4SQ(venue)

    # Exporter.py module
    # Output the Geopoints into `key`.json files

    print(f'~ Working with MongoDB: {category_set}')

    def to_MongoDB(category_set, category_set_cluster):
        """
        Takes a set of keys, and a cluster of key:data
        """
        client = MongoClient('mongodb://localhost/companies')
        db = client.get_database()
        
        for key in category_set:
            
            print(f" ~ Printing key: {key}")
            response = category_set_cluster[key]

            print(f" ~ Printing response.json(): {response.json()}")
            venues = response.json()['response']['venues']
            print(list(venues_to_GeoPoints(venues)))
            
            #GeoPoint = GeopointFrom4SQ(venue)
            if len(list(venues_to_GeoPoints(venues))) > 0:
                print(" ~ MONGODB - INSERTING MANY")
                db.geo_data.insert_many(list(venues_to_GeoPoints(venues)))
            else:
                print('=== empty venues')
            #Export the places to a json
            #ith open(f'{key}.json', 'w', encoding='utf-8') as f:c
            #  json.dump(Geopoint,f, ensure_ascii=False, indent=4)
                
            print(f"{type(response)}")
            
            print(f" ~ Printing response.json():")
            #print(f"{response.json()}")
            # for venue in response:
                #    print(f" ~ Printing venue: {venue}")
                # print(venue['name'],'\n', venue['location'])

    to_MongoDB(category_set, category_set_cluster)


# Now exporting some of that data to a json
client = MongoClient('mongodb://localhost/companies')
db = client.companies
collection = db.geo_data

import bson.json_util
print(' Exporting the MongoDB collection to Output folder ~')
cursor = collection.find({})
file = open("OUTPUT/geo_data.json", "w")
file.write('[')
for document in cursor:
    file.write(bson.json_util.dumps(document))
    file.write(',')
file.write(']')


print(' see you again soon ~')