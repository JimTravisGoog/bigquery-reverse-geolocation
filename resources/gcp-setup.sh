# sets up GCP specific products and publishes to pub/sub 
python create-env.py
bq mk sandiego_freeways
bq mk --schema geocoded_journeys.json sandiego_freeways.geocoded_journeys
python  config_geo_pubsub.py