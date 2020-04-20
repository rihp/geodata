from dotenv import load_dotenv
load_dotenv()

import requests
import json
import os

def geocode(address):
    '''
    Use geocode api to do forward geocoding. https://geocode.xyz/api
    INPUT:
        - A string address
    OUTPUT:
        - A GeoPoint dict 
    '''
    #res = requests.get(f"https://geocode.xyz/{address}&auth={os.getenv('GEOCODE')}",params={"json":1})
    res = requests.get(f"https://geocode.xyz/{address}",params={"json":1})

    data = res.json()
    print(res)
    # Return as GeoJSON -> https://geojson.org/
    return {
        "type":"Point",
        "coordinates": [float(data["longt"]), float(data["latt"])]
            }

# Watch how to handle the radius of the query
# call it only once for each category set.
def getCategoryFrom4SQ(ll, venue_category, radius=20000, limit=10):
    """
    A basic querying function that 
    INPUTS: 
       - the venue_category name, as defined by FOURSQUARE API.
    OUTPUT:
       - an array of GeoPoints
    """
    #Using the `/venues/search` enpoint
    url = 'https://api.foursquare.com/v2/venues/search'

    if type(venue_category) is str:
        # Define a dictionary with the venue categories ID
        # https://developer.foursquare.com/docs/build-with-foursquare/categories/
        #
        # ♠ OPTIMIZATION IDEA: Scrape the official website to build the complete dictionary
        #    and save it in a separate categories.py that can also filter correct categories
        #    and also generate mixed categories (Meaning, getting 'international transport' 
        #    to include heliports and airports in just one search.)
        relevant_categories = {'daycare':       '5744ccdfe4b0c0459246b4c7',
                               'preschool':     '52e81612bcbc57f1066b7a45',
                               'elementary school':'4f4533804b9074f6e4fb0105',
                               'middle school': '4f4533814b9074f6e4fb0106',
                               'high school':   '4bf58dd8d48988d13d941735',
                               
                               'coffee shop':   '4bf58dd8d48988d1e0931735',
                               'corporate coffee shop':'5665c7b9498e7d8a4f2c0f06', # More similar categories
                               
                               'airport':        '4bf58dd8d48988d1ed931735',
                               'heliport':       '56aa371ce4b08b9a8d57356e',
                               
                               'convention center':'4bf58dd8d48988d1ff931735',
                               'business center': '56aa371be4b08b9a8d573517',
                               
                               'design studio': '4bf58dd8d48988d1f4941735',
                               
                               'nightlife spot':'4d4b7105d754a06376d81259',
                               'arcade':        '4bf58dd8d48988d1e1931735',
                               
                               'tech startup':  '4bf58dd8d48988d125941735',
                               'coworking space':'4bf58dd8d48988d174941735',
                               'basketball court': '4bf58dd8d48988d1e1941735'
                              }
        
        venue_category_ID = relevant_categories[venue_category]
    else: 
        raise TypeError('You must use one of the predefined keys from the relevant_categories dictionary.')    
    


    # Set API Query parameters
    params = dict(
        client_id=os.getenv('FSQCLID'),
        client_secret=os.getenv('FSQCLSC'),
        v='20190323',   # This `v` should not be changed, untill API is to be re-developed, 
                        #  see: https://developer.foursquare.com/docs/places-api/versioning/
        ll=ll, # format : '40.7243,-74.0018'
        query=None,
        categoryId=venue_category_ID,
        radius=radius,
        limit=limit
    )

    print(f"Requesting: {url},    venue_category: {venue_category}" )
    response = requests.get(url=url, params=params)
    
    print(response.status_code) #https://http.cat/

    return response

def cluster_request(ll, category_set):
    """
    Define a function that makes multiple categorized requests to the API,
    and receive each request's RESPONSES in an interesting format:
      INPUT
        - An set of Foursquare categories: https://developer.foursquare.com/docs/api-reference/venues/categories/
      OUTPUT
        - The len(array) of Input == len(dict.keys) of Output
        - A Dictionary with each Foursquare Category as a key, and the resquests' response as its value
        - The dict.values will be the response generated from the enricher.py module
    """
    results = {}
    for category in category_set:
        results[category] = getCategoryFrom4SQ(ll,category, radius=20000)
    return results

def GeopointFrom4SQ(venue):
        """
          ##################################
        #################################
                
            IMPORTANT STEP !!!
            Formatting the output data
        

        INPUT: 
        - A single FourSquare API venue `blob`
        OUTPUT:
        - A correctly formatted `blob` for future use and export downstream
            'venue_location': dict(PointCategory and GeoPoint)
        
        """
        loc = venue['location']
        return {'venue_location':{ 
                    'name':venue['name'],     
                    'GeoPoint':{
                        'type':'Point',
                        'coordinates':[
                            loc['lng'],
                            loc['lat']
                        ]
                    },
                    'PointCategory':{"source":'4square location',
                                    # commented this out, to change the representation of the categories. I want a string, not an array of arrays
                                    # 'categories_names':[ venue['categories'][i]['name']    for i in range(len(venue['categories']))  ], 
                                    'categories_names': venue['categories'][0]['name'], 
                                    'categories_raw':venue['categories'],
                                    'formattedAddress':venue['location']['formattedAddress'],
                    }
                }
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


# INPUT:
# - A pandas row from a dataframe with geo
# OUTPUT:
# - A Tupple with:
#     -`GeoPoint` or `None`
#     - A string with an error message

# This function will process the values in that row, and return from it a
