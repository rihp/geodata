from dotenv import load_dotenv
load_dotenv()

import os
import enricher
import datetime


def say_hi():
    print(f"""
    -----------------------
    Welcome to Vesuvius 
    Version Alpha 001 
    -----------------------
    Today is {datetime.date.today()}

    """)

say_hi()
datetime.datetime.today()

# I have to make a function to melts Geopoints into 4SQ `ll` format
# This will be the cluster points generated from the crunchbase dataset
ll ='40.7243,-74.0018'

# Define a function that makes multiple categorized requests to the API,
# and receive each request's RESPONSES in an interesting format:
#   OUTPUT will be a DICT
#      - Each key of the output will be one of the keys from the input
#      - The len(array) of Input == len(dict.keys) of Output
#      - The dict.values will be the response generated from the enricher.py module
def cluster_request(cluster):
    results = {}
    for category in cluster:
        results[category] = enricher.getCategoryFrom4SQ(ll,category)
    return results

# Call the function
flight_points = ['airport', 'heliport']
flight_points_cluster = cluster_request(flight_points)

# Print the outcome completely
print(f"\n\n`flight_points_cluster`, raw variable:\n     {flight_points_cluster}")



# Print unwinded data
print(" ~ Printing unwinded data")
""" MUTED FOR IMPROVEMENTS
for key in flight_points:
    print(f" ~ Printing key: {key}")

    for response in flight_points_cluster[key]:
        print(f" ~ Printing response.json(): {response.contents()}")
       # for venue in response:
        #    print(f" ~ Printing venue: {venue}")
           # print(venue['name'],'\n', venue['location'])
"""


# Loop the categories defined earlier as they keys to our `cluster` dictionary
for key in flight_points:
    #print(f" ~ Printing type() of `flight_point_cluster[{key}]`: ")
    response = flight_points_cluster[key]
    #print(f"{type(response)}")

    #print(f" ~ Printing response.json():")
    print(f"{response.json()}")
       # for venue in response:
        #    print(f" ~ Printing venue: {venue}")
           # print(venue['name'],'\n', venue['location'])
