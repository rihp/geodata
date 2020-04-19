import os, datetime, json, requests
from dotenv import load_dotenv
from pymongo import MongoClient
import enricher, presenter

load_dotenv()
presenter.say_hi()

address = 'Caracas, Venezuela'
coords = enricher.geocode(address)

# I have to make a function to melt Geopoints into 4SQ `ll` format
# This will be the cluster points generated from the crunchbase dataset
ll = coords
ll = f"{ll['coordinates'][1]},{ll['coordinates'][0]}"
#ll = '40.37417177212408,-3.7015647782170413' # Madrid
#ll ='40.7243,-74.0018' # NYC

# IMPORTANT: ♠ This will change later to a list of categories which will be funnelled and output as GeoPoints
# Assign the categories we will look for to sets
kids_points = ['daycare', 'park']
party_points = ['convention center', 'nightlife spot']
flight_points = ['airport', 'heliport']


# Call the new function
category_set = flight_points
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
            'category':venue['categories'][0]['name'], 
            'GeoPoint':{
                'type':'Point',       
                'coordinates':[
                    loc['lng'],
                    loc['lat']
                ]
    }}

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
client = MongoClient('mongodb://localhost/companies')
db = client.get_database()
def to_MongoDB(category_set, category_set_cluster):
    for key in category_set:
        
        print(f" ~ Printing key: {key}")
        response = category_set_cluster[key]

        print(f" ~ Printing response.json(): {response.json()}")
        venues = response.json()['response']['venues']
        print(list(venues_to_GeoPoints(venues)))
        
        #GeoPoint = GeopointFrom4SQ(venue)
        if len(list(venues_to_GeoPoints(venues))) >0:
            print(" ~ MONGODB - INSERTING MANY")
            db.geo_lake.insert_many(list(venues_to_GeoPoints(venues)))
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