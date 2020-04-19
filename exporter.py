import bson.json_util
import os, datetime, json, requests
from pymongo import MongoClient
import enricher

def to_json(category_set, category_set_cluster):
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


# Output the Geopoints into `key`.json files
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
        print(list(enricher.venues_to_GeoPoints(venues)))
        
        #GeoPoint = GeopointFrom4SQ(venue)
        if len(list(enricher.venues_to_GeoPoints(venues))) > 0:
            print(" ~ MONGODB - INSERTING MANY")
            db.geo_data.insert_many(list(enricher.venues_to_GeoPoints(venues)))
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



def dump_array_of_dicts():
    """
    Connects to MongoDB, selects a collection, and writes a dump cache of the data
    """
    print(' ~ Now exporting the MongoDB to a json array of dicts')
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