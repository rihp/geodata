from dotenv import load_dotenv
load_dotenv()

import requests
import json
import os




def getCategoryFrom4SQ(ll, venue_category, radius='4000', limit=10):
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
        relevant_categories = {'daycare':         '5744ccdfe4b0c0459246b4c7',
                               
                               'coffee shop':    '4bf58dd8d48988d1e0931735',
                               'corporate coffee shop':'5665c7b9498e7d8a4f2c0f06', # More similar categories
                               
                               'airport':        '4bf58dd8d48988d1ed931735',
                               'heliport':       '56aa371ce4b08b9a8d57356e',
                               
                               'convention center':'4bf58dd8d48988d1ff931735',
                               'business center': '56aa371be4b08b9a8d573517',
                               
                               'design studio':'4bf58dd8d48988d1f4941735',
                               
                               'nightlife spot':'4d4b7105d754a06376d81259',
                               'arcade':       '4bf58dd8d48988d1e1931735',
                               
                               'volcano':      '5032848691d4c4b30a586d61',
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




# INPUT:
# - A pandas row from a dataframe with geo
# OUTPUT:
# - A Tupple with:
#     -`GeoPoint` or `None`
#     - A string with an error message

# This function will process the values in that row, and return from it a
