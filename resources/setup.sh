# setup.sh
mkdir /tmp/creds
bq mk sandiego_freeways
bq mk --schema geocoded_journeys.json sandiego_freeways.geocoded_journeys
mkdir /tmp/creds/data
cp resources/data/* /tmp/creds/data/
cp resources/setup.yaml /tmp/creds/
