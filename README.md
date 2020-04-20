# geodata
Selecting the best place in the world to build the offices for a gaming start-up.

![TOP LOCATION, at South San Francisco, California, USA]('OUTPUT/top_location.png')

This project is structured so that it takes some company data, filters 'relevant companies', and extracts their office locations as a GeoPoint.

Such GeoPoints are then added to a MongoDB collection, which will later be used to query the FourSquare API to gather relevant information about the venues surrounding the `relevant company's office`. 

At this stage, we are looking for places such as:
    - kindergarten
    - nightlife spots
    - airports

The output of this project includes a filtered dataset, and a suggestion of optimal places.
